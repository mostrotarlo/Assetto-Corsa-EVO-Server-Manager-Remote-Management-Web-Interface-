"""Shared configuration helpers for the control panel and background engine."""

from __future__ import annotations

import json
import os
import sys


APP_VERSION = "v1.5.0"
CONFIG_NAME = "app_config.json"

DEFAULT_CONFIG = {
    "password": "admin",
    "evo_path": "",
    "host": "0.0.0.0",
    "port": 5000,
    "base_path": "",
    "public_url": "",
    "disable_auth": False,
    "restore_running_on_startup": False,
    "watchdog_enabled": False,
    "watchdog_interval_sec": 30,
    "watchdog_max_restarts": 2,
    "watchdog_window_min": 10,
    "start_with_windows": False,
    "run_as_windows_service": False,
}


def app_dir() -> str:
    """Return the folder containing the installed executables or source files."""
    if getattr(sys, "frozen", False):
        return os.path.dirname(sys.executable)
    return os.path.dirname(os.path.abspath(__file__))


def config_path() -> str:
    return os.path.join(app_dir(), CONFIG_NAME)


def load_config() -> dict:
    data = {}
    path = config_path()
    if os.path.exists(path):
        try:
            with open(path, "r", encoding="utf-8") as handle:
                data = json.load(handle)
        except (OSError, ValueError, TypeError):
            data = {}

    for key, value in DEFAULT_CONFIG.items():
        data.setdefault(key, value)
    return data


def save_config(config: dict) -> None:
    data = dict(DEFAULT_CONFIG)
    data.update(config)
    path = config_path()
    temporary = path + ".tmp"
    with open(temporary, "w", encoding="utf-8") as handle:
        json.dump(data, handle, indent=2, ensure_ascii=False)
    os.replace(temporary, path)
