"""Windows control panel for EVO Web Server Manager.

The control panel never hosts the web application itself. It configures and
starts the separate background engine directly, at logon, or as a service.
"""

from __future__ import annotations

import ctypes
import os
import socket
import subprocess
import sys
import tkinter as tk
import webbrowser
from tkinter import filedialog, messagebox

from config_store import APP_VERSION, app_dir, load_config, save_config


BASE_DIR = app_dir()
SERVICE_NAME = "EvoWebServerManager"
ENGINE_EXE_NAME = "EVO Web Server Manager Engine.exe"
PID_FILE = os.path.join(BASE_DIR, "engine.pid")

WOACC_URL = "https://woacc.zapto.org/"
WOACC_TRACKER_URL = "https://woacc.zapto.org/tracker/"
WOACC_TRACKER_GITHUB_URL = "https://github.com/mostrotarlo/woacc-evo-tracker"


def engine_command(console: bool = False) -> list[str]:
    if getattr(sys, "frozen", False):
        command = [os.path.join(BASE_DIR, ENGINE_EXE_NAME)]
    else:
        command = [sys.executable, os.path.join(BASE_DIR, "backend_engine.py")]
    if console:
        command.append("--console")
    return command


def control_command() -> tuple[str, str]:
    if getattr(sys, "frozen", False):
        return sys.executable, "--autostart"
    return sys.executable, f'"{os.path.abspath(__file__)}" --autostart'


def startup_shortcut_path() -> str:
    startup_dir = os.path.join(
        os.environ.get("APPDATA", ""),
        r"Microsoft\Windows\Start Menu\Programs\Startup",
    )
    return os.path.join(startup_dir, "EVO Web Server Manager.lnk")


def set_start_with_windows(enabled: bool) -> None:
    shortcut = startup_shortcut_path()
    os.makedirs(os.path.dirname(shortcut), exist_ok=True)
    if not enabled:
        if os.path.exists(shortcut):
            os.remove(shortcut)
        return

    target, arguments = control_command()
    escaped_arguments = arguments.replace('"', '`"')
    ps = (
        "$shell = New-Object -ComObject WScript.Shell\n"
        f'$shortcut = $shell.CreateShortcut("{shortcut}")\n'
        f'$shortcut.TargetPath = "{target}"\n'
        f'$shortcut.Arguments = "{escaped_arguments}"\n'
        f'$shortcut.WorkingDirectory = "{BASE_DIR}"\n'
        "$shortcut.Save()\n"
    )
    subprocess.run(
        ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", ps],
        check=True,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )


def service_state() -> str:
    completed = subprocess.run(
        ["sc.exe", "query", SERVICE_NAME],
        check=False,
        capture_output=True,
        text=True,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    if completed.returncode:
        return "not installed"
    output = (completed.stdout + completed.stderr).upper()
    if "RUNNING" in output:
        return "running"
    if "STOPPED" in output:
        return "stopped"
    if "START_PENDING" in output:
        return "starting"
    if "STOP_PENDING" in output:
        return "stopping"
    return "installed"


def engine_is_listening(config: dict) -> bool:
    try:
        with socket.create_connection(("127.0.0.1", int(config.get("port", 5000))), timeout=0.25):
            return True
    except (OSError, ValueError):
        return False


def start_direct_engine(config: dict) -> bool:
    if service_state() == "running" or engine_is_listening(config):
        return False
    command = engine_command(console=True)
    creation_flags = (
        getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        | getattr(subprocess, "DETACHED_PROCESS", 0)
        | getattr(subprocess, "CREATE_NO_WINDOW", 0)
    )
    subprocess.Popen(
        command,
        cwd=BASE_DIR,
        stdin=subprocess.DEVNULL,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        close_fds=True,
        creationflags=creation_flags,
    )
    return True


def stop_direct_engine() -> bool:
    try:
        with open(PID_FILE, "r", encoding="ascii") as handle:
            pid = int(handle.read().strip())
    except (OSError, ValueError):
        return False
    completed = subprocess.run(
        ["taskkill", "/PID", str(pid), "/F"],
        check=False,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
    )
    return completed.returncode == 0


def run_engine_elevated(argument: str) -> bool:
    command = engine_command(console=False)
    executable = command[0]
    arguments = " ".join([*(f'"{item}"' for item in command[1:]), argument])
    result = ctypes.windll.shell32.ShellExecuteW(
        None, "runas", executable, arguments, BASE_DIR, 1
    )
    return result > 32


def local_url(config: dict) -> str:
    base_path = (config.get("base_path") or "").rstrip("/")
    return f"http://127.0.0.1:{int(config.get('port', 5000))}{base_path}/"


def preferred_url(config: dict) -> str:
    return (config.get("public_url") or "").strip().rstrip("/") or local_url(config)


def autostart_mode() -> int:
    config = load_config()
    if not config.get("run_as_windows_service"):
        start_direct_engine(config)
    return 0


if "--autostart" in sys.argv:
    raise SystemExit(autostart_mode())


config = load_config()
root = tk.Tk()
root.title(f"EVO Web Server Manager Control Panel {APP_VERSION}")
root.resizable(False, False)
pad = {"padx": 8, "pady": 6}

tk.Label(root, text=f"EVO Web Server Manager {APP_VERSION}", font=("Segoe UI", 12, "bold")).grid(
    row=0, column=0, columnspan=3, sticky="w", padx=8, pady=(10, 2)
)
tk.Label(root, text="Control panel for the separate background Engine", fg="#555").grid(
    row=1, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8)
)

tk.Label(root, text="Login password").grid(row=2, column=0, sticky="w", **pad)
password_entry = tk.Entry(root, width=36, show="*")
password_entry.insert(0, config.get("password", "admin"))
password_entry.grid(row=2, column=1, **pad)

tk.Label(root, text="EVO Dedicated Server folder").grid(row=3, column=0, sticky="w", **pad)
path_entry = tk.Entry(root, width=52)
path_entry.insert(0, config.get("evo_path", ""))
path_entry.grid(row=3, column=1, **pad)


def browse() -> None:
    selected = filedialog.askdirectory(title="Select Assetto Corsa EVO Dedicated Server folder")
    if selected:
        path_entry.delete(0, "end")
        path_entry.insert(0, selected)


tk.Button(root, text="Browse", command=browse).grid(row=3, column=2, **pad)

tk.Label(root, text="Base path").grid(row=4, column=0, sticky="w", **pad)
base_path_entry = tk.Entry(root, width=36)
base_path_entry.insert(0, config.get("base_path", ""))
base_path_entry.grid(row=4, column=1, sticky="w", **pad)
tk.Label(root, text="Example: /evo when using Caddy subpath").grid(row=4, column=2, sticky="w", **pad)

tk.Label(root, text="Public URL").grid(row=5, column=0, sticky="w", **pad)
public_url_entry = tk.Entry(root, width=52)
public_url_entry.insert(0, config.get("public_url", ""))
public_url_entry.grid(row=5, column=1, **pad)
tk.Label(root, text="Optional. Example: https://woacc.zapto.org/evo").grid(row=5, column=2, sticky="w", **pad)

disable_auth_var = tk.BooleanVar(value=bool(config.get("disable_auth", False)))
restore_var = tk.BooleanVar(value=bool(config.get("restore_running_on_startup", False)))
watchdog_var = tk.BooleanVar(value=bool(config.get("watchdog_enabled", False)))
startup_var = tk.BooleanVar(value=bool(config.get("start_with_windows", False)))
service_var = tk.BooleanVar(value=bool(config.get("run_as_windows_service", False)))


def select_startup_mode() -> None:
    if startup_var.get():
        service_var.set(False)


def select_service_mode() -> None:
    if service_var.get():
        startup_var.set(False)


tk.Checkbutton(root, text="Disable web authentication", variable=disable_auth_var).grid(
    row=6, column=0, columnspan=2, sticky="w", padx=8, pady=2
)
tk.Label(root, text="Use only with external auth or trusted LAN", fg="#777").grid(
    row=6, column=2, sticky="w", padx=8, pady=2
)
tk.Checkbutton(root, text="Restore previously running servers on startup", variable=restore_var).grid(
    row=7, column=0, columnspan=2, sticky="w", padx=8, pady=2
)
tk.Checkbutton(root, text="Enable server watchdog", variable=watchdog_var).grid(
    row=8, column=0, columnspan=2, sticky="w", padx=8, pady=2
)
tk.Checkbutton(
    root, text="Start Engine with Windows after user sign-in", variable=startup_var, command=select_startup_mode
).grid(row=9, column=0, columnspan=2, sticky="w", padx=8, pady=2)
tk.Checkbutton(
    root, text="Run Engine as a Windows service before user sign-in", variable=service_var, command=select_service_mode
).grid(row=10, column=0, columnspan=2, sticky="w", padx=8, pady=2)
tk.Label(root, text="Service installation requires administrator approval", fg="#777").grid(
    row=10, column=2, sticky="w", padx=8, pady=2
)

status_var = tk.StringVar(value="Checking Engine status...")
tk.Label(root, textvariable=status_var, fg="#087a35").grid(
    row=11, column=0, columnspan=3, sticky="w", **pad
)


def collect_config() -> dict:
    updated = dict(config)
    base_path = base_path_entry.get().strip()
    if base_path and not base_path.startswith("/"):
        base_path = "/" + base_path
    updated.update({
        "password": password_entry.get().strip() or "admin",
        "evo_path": path_entry.get().strip(),
        "host": "0.0.0.0",
        "port": 5000,
        "base_path": base_path.rstrip("/"),
        "public_url": public_url_entry.get().strip(),
        "disable_auth": bool(disable_auth_var.get()),
        "restore_running_on_startup": bool(restore_var.get()),
        "watchdog_enabled": bool(watchdog_var.get()),
        "start_with_windows": bool(startup_var.get()),
        "run_as_windows_service": bool(service_var.get()),
    })
    return updated


def save_settings(show_confirmation: bool = True) -> dict | None:
    global config
    previous_service = bool(config.get("run_as_windows_service"))
    updated = collect_config()
    try:
        save_config(updated)
        set_start_with_windows(updated["start_with_windows"] and not updated["run_as_windows_service"])
    except OSError as exc:
        messagebox.showerror("Save settings", f"Unable to save settings:\n{exc}")
        return None

    config = updated
    if updated["run_as_windows_service"] and service_state() == "not installed":
        if not run_engine_elevated("--install-start"):
            messagebox.showerror("Windows service", "Unable to request administrator approval.")
    elif previous_service and not updated["run_as_windows_service"]:
        if not run_engine_elevated("--remove-service"):
            messagebox.showerror("Windows service", "Unable to request administrator approval.")

    if show_confirmation:
        messagebox.showinfo(
            "Settings saved",
            "Settings saved. Restart the Engine to apply changes that affect the web service.",
        )
    root.after(1500, refresh_status)
    return updated


def start_or_restart() -> None:
    install_requested = bool(service_var.get()) and service_state() == "not installed"
    updated = save_settings(show_confirmation=False)
    if updated is None:
        return
    if install_requested:
        # save_settings has already launched one elevated install-and-start sequence.
        root.after(1800, refresh_status)
        return
    state = service_state()
    if updated.get("run_as_windows_service") or state != "not installed":
        argument = "--restart-service" if state == "running" else "start"
        if not run_engine_elevated(argument):
            messagebox.showerror("Windows service", "Unable to request administrator approval.")
    else:
        start_direct_engine(updated)
    root.after(1800, refresh_status)


def stop_engine() -> None:
    if service_state() != "not installed":
        if not run_engine_elevated("stop"):
            messagebox.showerror("Windows service", "Unable to request administrator approval.")
    elif not stop_direct_engine():
        messagebox.showinfo("Stop Engine", "No directly started Engine process was found.")
    root.after(1500, refresh_status)


def open_web() -> None:
    webbrowser.open(preferred_url(collect_config()))


def refresh_status() -> None:
    state = service_state()
    listening = engine_is_listening(config)
    if state != "not installed":
        status_var.set(f"Windows service: {state}")
    elif listening:
        status_var.set("Engine: running directly")
    else:
        status_var.set("Engine: stopped")
    root.after(2500, refresh_status)


button_frame = tk.Frame(root)
button_frame.grid(row=12, column=0, columnspan=3, pady=12)
tk.Button(button_frame, text="Save Settings", command=save_settings, width=18).grid(row=0, column=0, padx=4)
tk.Button(button_frame, text="Start / Restart Engine", command=start_or_restart, width=22).grid(row=0, column=1, padx=4)
tk.Button(button_frame, text="Stop Engine", command=stop_engine, width=16).grid(row=0, column=2, padx=4)
tk.Button(button_frame, text="Open Web Interface", command=open_web, width=20).grid(row=0, column=3, padx=4)

promo_frame = tk.LabelFrame(root, text="WOACC Community & Tools", padx=8, pady=8)
promo_frame.grid(row=13, column=0, columnspan=3, sticky="we", padx=8, pady=(4, 10))
tk.Label(
    promo_frame, text="WOACC EVO Tracker is an optional separate project available for download.", fg="#333"
).grid(row=0, column=0, columnspan=3, sticky="w", pady=(0, 6))
tk.Button(promo_frame, text="Open WOACC Community", command=lambda: webbrowser.open(WOACC_URL), width=24).grid(
    row=1, column=0, padx=4, pady=4
)
tk.Button(
    promo_frame, text="WOACC EVO Tracker (Example)", command=lambda: webbrowser.open(WOACC_TRACKER_URL), width=24
).grid(row=1, column=1, padx=4, pady=4)
tk.Button(promo_frame, text="Tracker GitHub", command=lambda: webbrowser.open(WOACC_TRACKER_GITHUB_URL), width=24).grid(
    row=1, column=2, padx=4, pady=4
)

tk.Label(root, text="Closing this window does not stop the Engine or dedicated servers.", fg="#777").grid(
    row=14, column=0, columnspan=3, sticky="w", padx=8, pady=(0, 8)
)

refresh_status()
root.mainloop()
