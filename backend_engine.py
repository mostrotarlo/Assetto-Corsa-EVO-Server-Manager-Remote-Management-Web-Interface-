"""Headless engine for EVO Web Server Manager.

This executable owns the web interface, watchdog and dedicated-server
processes.  It can run as a normal background process or as a Windows service.
"""

from __future__ import annotations

import logging
import os
import signal
import subprocess
import sys

from config_store import APP_VERSION, app_dir, load_config
from web_server import run_web, stop_web


SERVICE_NAME = "EvoWebServerManager"
SERVICE_DISPLAY_NAME = "EVO Web Server Manager Engine"
SERVICE_DESCRIPTION = "Runs the EVO web interface, watchdog and dedicated servers."
PID_FILE = os.path.join(app_dir(), "engine.pid")
LOG_FILE = os.path.join(app_dir(), "engine.log")


def configure_logging() -> None:
    logging.basicConfig(
        filename=LOG_FILE,
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        encoding="utf-8",
    )


def write_pid() -> None:
    with open(PID_FILE, "w", encoding="ascii") as handle:
        handle.write(str(os.getpid()))


def remove_pid() -> None:
    try:
        with open(PID_FILE, "r", encoding="ascii") as handle:
            stored_pid = int(handle.read().strip())
        if stored_pid == os.getpid():
            os.remove(PID_FILE)
    except (OSError, ValueError):
        pass


def request_stop(*_args) -> None:
    stop_web()


def run_engine() -> None:
    os.chdir(app_dir())
    configure_logging()
    write_pid()
    logging.info("Starting EVO Web Server Manager Engine %s", APP_VERSION)

    for signal_name in ("SIGINT", "SIGTERM", "SIGBREAK"):
        current_signal = getattr(signal, signal_name, None)
        if current_signal is not None:
            try:
                signal.signal(current_signal, request_stop)
            except (OSError, ValueError):
                pass

    try:
        run_web(load_config())
    except Exception:
        logging.exception("The background engine stopped unexpectedly")
        raise
    finally:
        remove_pid()
        logging.info("EVO Web Server Manager Engine stopped")


try:
    import servicemanager
    import win32event
    import win32service
    import win32serviceutil
except ImportError:
    servicemanager = None
    win32event = None
    win32service = None
    win32serviceutil = None


if win32serviceutil is not None:
    class EvoManagerService(win32serviceutil.ServiceFramework):
        _svc_name_ = SERVICE_NAME
        _svc_display_name_ = SERVICE_DISPLAY_NAME
        _svc_description_ = SERVICE_DESCRIPTION

        def __init__(self, args):
            super().__init__(args)
            self.stop_event = win32event.CreateEvent(None, 0, 0, None)

        def SvcStop(self):
            self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
            stop_web()
            win32event.SetEvent(self.stop_event)

        def SvcDoRun(self):
            servicemanager.LogInfoMsg(f"{SERVICE_DISPLAY_NAME} {APP_VERSION} starting")
            try:
                run_engine()
            except Exception as exc:
                servicemanager.LogErrorMsg(f"{SERVICE_DISPLAY_NAME} failed: {exc}")
                raise


def run_elevated_service_sequence(commands: list[list[str]]) -> int:
    """Execute standard pywin32 service commands from one elevated process."""
    for arguments in commands:
        completed = subprocess.run([sys.executable, *arguments], check=False)
        if completed.returncode:
            return completed.returncode
    return 0


def service_command() -> int:
    if win32serviceutil is None:
        print("Windows service support is unavailable. Install pywin32.", file=sys.stderr)
        return 2

    command = sys.argv[1] if len(sys.argv) > 1 else ""
    if command == "--install-start":
        return run_elevated_service_sequence([
            ["--startup", "auto", "install"],
            ["start"],
        ])
    if command == "--remove-service":
        # Stopping an already stopped service can fail; removal is still attempted.
        subprocess.run([sys.executable, "stop"], check=False)
        return subprocess.run([sys.executable, "remove"], check=False).returncode
    if command == "--restart-service":
        subprocess.run([sys.executable, "stop"], check=False)
        return subprocess.run([sys.executable, "start"], check=False).returncode

    win32serviceutil.HandleCommandLine(EvoManagerService)
    return 0


def main() -> int:
    if "--console" in sys.argv:
        run_engine()
        return 0
    return service_command()


if __name__ == "__main__":
    raise SystemExit(main())
