"""Graphical migration installer for EVO Web Server Manager v1.5.0."""

from __future__ import annotations

import shutil
import subprocess
import sys
import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox

APP_VERSION = "v1.5.0"
NEW_FILES = (
    "EVO Web Server Manager Control Panel.exe",
    "EVO Web Server Manager Engine.exe",
    "EVO Web Server Manager Manual.pdf",
)
LEGACY_EXACT = {"EVO Web Server Manager.exe"}


def resource_dir() -> Path:
    return Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent)) / "payload"


def legacy_executables(folder: Path) -> list[Path]:
    result = []
    for candidate in folder.glob("*.exe"):
        lower = candidate.name.lower()
        if candidate.name in LEGACY_EXACT or lower.startswith("evo web server manager v1.4"):
            result.append(candidate)
    return sorted(result, key=lambda item: item.name.lower())


def looks_like_existing_install(folder: Path) -> bool:
    return ((folder / "app_config.json").is_file() or (folder / "servers").is_dir()
            or bool(legacy_executables(folder)))


def migrate_folder(target: Path, source: Path) -> list[str]:
    """Copy the v1.5 files, then remove only recognized legacy executables."""
    for name in NEW_FILES:
        shutil.copy2(source / name, target / name)
    removed = []
    for old_executable in legacy_executables(target):
        removed.append(old_executable.name)
        old_executable.unlink()
    return removed


def install() -> None:
    target_text = target_var.get().strip()
    if not target_text:
        messagebox.showerror("Folder required", "Select the folder containing the previous version.")
        return
    target = Path(target_text).expanduser().resolve()
    if not target.is_dir():
        messagebox.showerror("Invalid folder", "The selected folder does not exist.")
        return
    if not looks_like_existing_install(target):
        messagebox.showerror(
            "Previous version not found",
            "The selected folder does not contain app_config.json, servers, or a recognized legacy executable.",
        )
        return
    source = resource_dir()
    missing = [name for name in NEW_FILES if not (source / name).is_file()]
    if missing:
        messagebox.showerror("Installer error", "Missing installer payload:\n" + "\n".join(missing))
        return
    legacy = legacy_executables(target)
    removal_text = "\n".join(path.name for path in legacy) or "No legacy executable was found."
    if not messagebox.askyesno(
        f"Install {APP_VERSION}",
        "The installer will preserve app_config.json, the servers folder, logs and results.\n\n"
        "It will copy the new Control Panel, Engine and manual.\n\n"
        f"Legacy executables to remove:\n{removal_text}\n\nContinue?",
    ):
        return
    try:
        migrate_folder(target, source)
    except PermissionError as exc:
        messagebox.showerror(
            "File in use",
            "Close the previous manager and the Control Panel, then run the installer again.\n\n"
            f"Windows message: {exc}",
        )
        return
    except OSError as exc:
        messagebox.showerror("Installation failed", str(exc))
        return
    launch = messagebox.askyesno(
        "Installation completed",
        f"EVO Web Server Manager {APP_VERSION} was installed successfully.\n\n"
        "Existing settings and servers were preserved.\n\nOpen the Control Panel now?",
    )
    if launch:
        subprocess.Popen([str(target / NEW_FILES[0])], cwd=target)
    root.destroy()


def browse() -> None:
    selected = filedialog.askdirectory(title="Select the previous EVO Web Server Manager folder")
    if selected:
        target_var.set(selected)


def main() -> None:
    global root, target_var
    root = tk.Tk()
    root.title(f"EVO Web Server Manager {APP_VERSION} Installer")
    root.resizable(False, False)
    frame = tk.Frame(root, padx=22, pady=20)
    frame.grid(sticky="nsew")
    frame.columnconfigure(0, weight=1)
    tk.Label(frame, text=f"EVO Web Server Manager {APP_VERSION}", font=("Segoe UI", 14, "bold")).grid(
        row=0, column=0, columnspan=2, sticky="w", pady=(0, 8)
    )
    tk.Label(
        frame,
        text="Select the folder containing your previous version.\nYour settings and server folders will be preserved.",
        justify="left",
    ).grid(row=1, column=0, columnspan=2, sticky="w", pady=(0, 14))
    target_var = tk.StringVar()
    tk.Entry(frame, textvariable=target_var, width=64).grid(row=2, column=0, sticky="ew", padx=(0, 8))
    tk.Button(frame, text="Browse...", command=browse, width=12).grid(row=2, column=1)
    tk.Label(frame, text="Close the old application before continuing.", fg="#8a4b00").grid(
        row=3, column=0, columnspan=2, sticky="w", pady=(10, 18)
    )
    buttons = tk.Frame(frame)
    buttons.grid(row=4, column=0, columnspan=2, sticky="e")
    tk.Button(buttons, text="Cancel", command=root.destroy, width=12).pack(side="left", padx=(0, 8))
    tk.Button(buttons, text="Install", command=install, width=16).pack(side="left")
    root.mainloop()


if __name__ == "__main__":
    main()
