import json
import os
import sys
import threading
import webbrowser
import tkinter as tk
from tkinter import filedialog, messagebox


def app_dir() -> str:
    """Directory where config and user data are stored."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


BASE_DIR = app_dir()
os.chdir(BASE_DIR)

from web_server import run_web  # noqa: E402

CFG = os.path.join(BASE_DIR, "app_config.json")

DEFAULT_CFG = {
    "password": "admin",
    "evo_path": "",
    "host": "0.0.0.0",
    "port": 5000,
    "base_path": "",
    "public_url": ""
}


def save_cfg(cfg):
    with open(CFG, "w", encoding="utf-8") as f:
        json.dump(cfg, f, indent=2, ensure_ascii=False)


def load_cfg():
    data = {}

    if os.path.exists(CFG):
        try:
            with open(CFG, "r", encoding="utf-8") as f:
                data = json.load(f)
        except Exception:
            data = {}

    for k, v in DEFAULT_CFG.items():
        data.setdefault(k, v)

    save_cfg(data)
    return data


server_thread = None


def start_app(cfg):
    global server_thread

    save_cfg(cfg)

    if server_thread and server_thread.is_alive():
        messagebox.showinfo("EVO Web Server Manager", "Web app already running.")
        return

    server_thread = threading.Thread(target=run_web, args=(cfg,), daemon=True)
    server_thread.start()

    local_url = f"http://127.0.0.1:{cfg['port']}{cfg.get('base_path', '') or ''}/"
    open_url = (cfg.get("public_url") or "").strip().rstrip("/") or local_url

    status_var.set(f"Running on {open_url}")
    webbrowser.open(open_url)


root = tk.Tk()
root.title("EVO Web Server Manager Setup")
root.resizable(False, False)

cfg = load_cfg()

pad = {"padx": 8, "pady": 6}

# Password
tk.Label(root, text="Login password").grid(row=0, column=0, sticky="w", **pad)
pw = tk.Entry(root, width=36, show="*")
pw.insert(0, cfg.get("password", "admin"))
pw.grid(row=0, column=1, **pad)

# EVO path
tk.Label(root, text="EVO Dedicated Server folder").grid(row=1, column=0, sticky="w", **pad)
path = tk.Entry(root, width=52)
path.insert(0, cfg.get("evo_path", ""))
path.grid(row=1, column=1, **pad)


def browse():
    selected = filedialog.askdirectory(title="Select Assetto Corsa EVO Dedicated Server folder")
    if selected:
        path.delete(0, "end")
        path.insert(0, selected)


tk.Button(root, text="Browse", command=browse).grid(row=1, column=2, **pad)

# Base path
tk.Label(root, text="Base path").grid(row=2, column=0, sticky="w", **pad)
base_path = tk.Entry(root, width=36)
base_path.insert(0, cfg.get("base_path", ""))
base_path.grid(row=2, column=1, sticky="w", **pad)
tk.Label(root, text="Example: /evo when using Caddy subpath").grid(row=2, column=2, sticky="w", **pad)

# Public URL
tk.Label(root, text="Public URL").grid(row=3, column=0, sticky="w", **pad)
public_url = tk.Entry(root, width=52)
public_url.insert(0, cfg.get("public_url", ""))
public_url.grid(row=3, column=1, sticky="w", **pad)
tk.Label(root, text="Optional. Example: https://woacc.zapto.org/evo").grid(row=3, column=2, sticky="w", **pad)

status_var = tk.StringVar(value="Stopped")
tk.Label(root, textvariable=status_var, fg="#0a7").grid(row=4, column=0, columnspan=3, sticky="w", **pad)


def go():
    cfg2 = dict(cfg)
    bp = base_path.get().strip()
    if bp and not bp.startswith("/"):
        bp = "/" + bp
    bp = bp.rstrip("/")

    cfg2["password"] = pw.get().strip() or "admin"
    cfg2["evo_path"] = path.get().strip()
    cfg2["host"] = "0.0.0.0"
    cfg2["port"] = 5000
    cfg2["base_path"] = bp
    cfg2["public_url"] = public_url.get().strip()

    start_app(cfg2)


tk.Button(root, text="Start Web App", command=go, width=22).grid(row=5, column=1, pady=12)

root.mainloop()
