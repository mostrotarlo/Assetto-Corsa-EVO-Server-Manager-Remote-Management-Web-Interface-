from flask import Flask, request, redirect, session, render_template
import os
import sys
import json
import shutil
import subprocess

CREATE_NO_WINDOW = 0
if os.name == "nt":
    CREATE_NO_WINDOW = subprocess.CREATE_NO_WINDOW

from evo_encoder import encode_evo_payload
from evo_mapper import build_serverconfig, build_seasondefinition

def resource_path(relative_path):
    """Path for bundled resources in PyInstaller and normal source mode."""
    if getattr(sys, "frozen", False):
        base = getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


def data_path(relative_path):
    """Writable path next to the exe/source folder."""
    if getattr(sys, "frozen", False):
        base = os.path.dirname(sys.executable)
    else:
        base = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base, relative_path)


app = Flask(__name__, template_folder=resource_path("templates"))
app.secret_key = "change-this-secret-key"

SERVERS_DIR = data_path("servers")
PIDS_FILE = data_path("running_servers.json")


# ============================================================
# BASE PATH / CADDY SUPPORT
# ============================================================

class PrefixMiddleware:
    def __init__(self, app, prefix=""):
        self.app = app
        self.prefix = prefix.rstrip("/")

    def __call__(self, environ, start_response):
        if self.prefix:
            path = environ.get("PATH_INFO", "")
            if path.startswith(self.prefix):
                environ["SCRIPT_NAME"] = self.prefix
                environ["PATH_INFO"] = path[len(self.prefix):] or "/"
        return self.app(environ, start_response)


def url(path="/"):
    base = app.config.get("BASE_PATH", "")
    if not path.startswith("/"):
        path = "/" + path
    return base + path


@app.context_processor
def inject_base_path():
    return {"BASE_PATH": app.config.get("BASE_PATH", "")}


# ============================================================
# PID / PROCESSI
# ============================================================

def load_pids():
    if os.path.exists(PIDS_FILE):
        try:
            with open(PIDS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def save_pids(data):
    with open(PIDS_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def is_pid_running(pid):
    try:
        out = subprocess.check_output(
            ["tasklist", "/FI", f"PID eq {pid}"],
            text=True,
            stderr=subprocess.DEVNULL,
            creationflags=CREATE_NO_WINDOW
        )
        return str(pid) in out
    except Exception:
        return False


# ============================================================
# PATH
# ============================================================

def server_path(server_id):
    return os.path.join(SERVERS_DIR, server_id)


def server_exe_path(server_id):
    return os.path.normpath(
        os.path.join(server_path(server_id), "AssettoCorsaEVOServer.exe")
    )


def server_config_path(server_id):
    return os.path.join(server_path(server_id), "server.json")


def load_json_file(path, default):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return default


# ============================================================
# SERVER CONFIG
# ============================================================

def load_server(server_id):
    with open(server_config_path(server_id), "r", encoding="utf-8") as f:
        return json.load(f)


def save_server(server_id, data):
    with open(server_config_path(server_id), "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def create_default_server(server_id, cfg):
    p = server_path(server_id)
    result_path = os.path.abspath(os.path.join(p, "result"))

    os.makedirs(p, exist_ok=True)
    os.makedirs(result_path, exist_ok=True)

    num = int(server_id.split("_")[-1])

    return {
        "id": server_id,
        "name": f"Server {num}",

        "tcp_port": 9700 + num - 1,
        "udp_port": 9700 + num - 1,
        "http_port": 8080 + num - 1,
        "max_players": 8,
        "cycle": True,

        "driver_password": "",
        "spectator_password": "",
        "admin_password": "admin",

        "entry_list_path": "",
        "results_path": result_path + "\\",

        "type": "MultiplayerServerListSessionType_RANKED",

        "game_type": "GameModeType_PRACTICE",
        "year": 2024,
        "month": 8,
        "day": 15,
        "second": 0,
        "export_json": False,

        "track": "Imola",
        "layout": "GP",
        "event_name": "GP Time Attack",
        "track_length": 4909,

        "weather": "GameModeSelectionWeatherType_CLEAR",
        "weather_behavior": "GameModeSelectionWeatherBehaviour_STATIC",
        "initial_grip": "InitialGrip_GREEN",

        "cars": [
            {
                "car_name": "preset_m4gt3_mech_1",
                "ballast": 0,
                "restrictor": 0.0
            }
        ],

        "practice_length": 300,
        "practice_hour": 16,
        "practice_minute": 0,
        "practice_time_multiplier": 1,
        "practice_max_wait_to_box": 10,
        "practice_overtime": 10,

        "qualify_length": 300,
        "qualify_hour": 16,
        "qualify_minute": 0,
        "qualify_time_multiplier": 1,
        "qualify_max_wait_to_box": 10,
        "qualify_overtime": 10,

        "warmup_length": 300,
        "warmup_hour": 16,
        "warmup_minute": 0,
        "warmup_time_multiplier": 1,
        "warmup_max_wait_to_box": 10,
        "warmup_overtime": 10,

        "race_length": 300,
        "race_duration_type": "GameModeSelectionDuration_TIME",
        "race_hour": 16,
        "race_minute": 0,
        "race_time_multiplier": 1,
        "race_max_wait_to_box": 10,
        "race_overtime": 10,
        "min_waiting_for_players": 10,
        "max_waiting_for_players": 30,

        # Optional full command copied from the official Kunos launcher.
        # If empty, the manager generates -serverconfig and -seasondefinition normally.
        "custom_command": ""
    }


# ============================================================
# WEB START
# ============================================================

def run_web(cfg):
    os.makedirs(SERVERS_DIR, exist_ok=True)

    base_path = cfg.get("base_path", "").rstrip("/")

    app.config["CFG"] = cfg
    app.config["BASE_PATH"] = base_path
    app.secret_key = cfg.get("secret_key") or ("evo-manager-" + str(cfg.get("password", "admin")))

    app.config["SESSION_COOKIE_PATH"] = "/"
    app.config["SESSION_COOKIE_SAMESITE"] = "Lax"

    # IMPORTANTE:
    # Secure=True solo se stai usando HTTPS pubblico dietro Caddy.
    # In locale HTTP deve essere False, altrimenti il login non resta salvato.
    public_url = cfg.get("public_url", "")
    use_https = public_url.startswith("https://")

    app.config["SESSION_COOKIE_SECURE"] = use_https

    from werkzeug.middleware.proxy_fix import ProxyFix

    if not hasattr(app, "_original_wsgi_app"):
        app._original_wsgi_app = app.wsgi_app

    app.wsgi_app = app._original_wsgi_app

    # 🔥 QUESTO RISOLVE TUTTO
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

    if base_path:
        app.wsgi_app = PrefixMiddleware(app.wsgi_app, base_path)

    app.run(host=cfg["host"], port=cfg["port"])


# ============================================================
# LOGIN
# ============================================================

@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        if request.form.get("pw") == app.config["CFG"]["password"]:
            session["ok"] = True
            return redirect(url("/dash"))

    return render_template("login.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dash")
def dash():
    if not session.get("ok"):
        return redirect(url("/"))

    pids = load_pids()
    servers = []

    for sid in os.listdir(SERVERS_DIR):
        spath = server_path(sid)

        if not os.path.isdir(spath):
            continue

        cfg_path = server_config_path(sid)

        if os.path.exists(cfg_path):
            data = load_server(sid)
        else:
            data = {"id": sid, "name": sid}

        pid = pids.get(sid)
        running = bool(pid and is_pid_running(pid))

        servers.append({
            "id": sid,
            "name": data.get("name", sid),
            "running": running,
            "pid": pid
        })

    return render_template("index.html", servers=servers)


# ============================================================
# ADD SERVER
# ============================================================

@app.route("/add")
def add():
    if not session.get("ok"):
        return redirect(url("/"))

    i = 1
    while True:
        server_id = f"server_{i}"
        dst = server_path(server_id)

        if not os.path.exists(dst):
            break

        i += 1

    src = app.config["CFG"]["evo_path"]

    if not os.path.isdir(src):
        return "EVO Dedicated Server path not valid"

    shutil.copytree(src, dst)

    os.makedirs(os.path.join(dst, "result"), exist_ok=True)

    data = create_default_server(server_id, app.config["CFG"])
    save_server(server_id, data)

    return redirect(url("/dash"))


# ============================================================
# SERVER DETAIL
# ============================================================

@app.route("/server/<server_id>")
def server_detail(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    data = load_server(server_id)
    return render_template("server.html", server=data)


# ============================================================
# SETTINGS PAGE
# ============================================================

@app.route("/server/<server_id>/settings")
def server_settings(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    data = load_server(server_id)
    base = server_path(server_id)

    cars_data = load_json_file(os.path.join(base, "cars.json"), {"cars": []})
    practice_events = load_json_file(os.path.join(base, "events_practice.json"), {"events": []})
    race_events = load_json_file(os.path.join(base, "events_race_weekend.json"), {"events": []})

    selected_car_names = {
        c.get("car_name")
        for c in data.get("cars", [])
    }

    selected_car_map = {
        c.get("car_name"): c
        for c in data.get("cars", [])
    }

    return render_template(
        "settings.html",
        server=data,
        cars=cars_data.get("cars", []),
        practice_events=practice_events.get("events", []),
        race_events=race_events.get("events", []),
        selected_car_names=selected_car_names,
        selected_car_map=selected_car_map
    )


@app.route("/server/<server_id>/settings/save", methods=["POST"])
def save_settings(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    data = load_server(server_id)

    data["name"] = request.form.get("name", data.get("name", "Server"))
    data["tcp_port"] = int(request.form.get("tcp_port", data.get("tcp_port", 9700)))
    data["udp_port"] = int(request.form.get("udp_port", data.get("udp_port", 9700)))
    data["http_port"] = int(request.form.get("http_port", data.get("http_port", 8080)))
    data["max_players"] = int(request.form.get("max_players", data.get("max_players", 8)))

    data["cycle"] = request.form.get("cycle") == "on"

    data["driver_password"] = request.form.get("driver_password", "")
    data["spectator_password"] = request.form.get("spectator_password", "")
    data["admin_password"] = request.form.get("admin_password", "")

    data["entry_list_path"] = request.form.get("entry_list_path", "")
    data["results_path"] = request.form.get("results_path", data.get("results_path", ""))
    data["custom_command"] = request.form.get("custom_command", "").strip()

    data["type"] = request.form.get("type", "MultiplayerServerListSessionType_RANKED")
    data["game_type"] = request.form.get("game_type", "GameModeType_PRACTICE")
    data["weather"] = request.form.get("weather", "GameModeSelectionWeatherType_CLEAR")
    data["weather_behavior"] = request.form.get("weather_behavior", "GameModeSelectionWeatherBehaviour_STATIC")
    data["initial_grip"] = request.form.get("initial_grip", "InitialGrip_GREEN")

    track_value = request.form.get("track_value", "")
    if track_value:
        parts = track_value.split("|")
        if len(parts) == 4:
            data["track"] = parts[0]
            data["layout"] = parts[1]
            data["event_name"] = parts[2]
            data["track_length"] = int(parts[3])

    # Practice settings
    data["practice_length"] = int(request.form.get("practice_length", data.get("practice_length", 300)))
    data["practice_hour"] = int(request.form.get("practice_hour", data.get("practice_hour", 16)))
    data["practice_minute"] = int(request.form.get("practice_minute", data.get("practice_minute", 0)))
    data["practice_time_multiplier"] = int(request.form.get("practice_time_multiplier", data.get("practice_time_multiplier", data.get("time_multiplier", 1))))
    data["practice_max_wait_to_box"] = int(request.form.get("practice_max_wait_to_box", data.get("practice_max_wait_to_box", data.get("max_wait_to_box", 10))))
    data["practice_overtime"] = int(request.form.get("practice_overtime", data.get("practice_overtime", data.get("overtime", 10))))

    # Race Weekend settings
    for prefix in ("qualify", "warmup", "race"):
        data[f"{prefix}_length"] = int(request.form.get(f"{prefix}_length", data.get(f"{prefix}_length", 300)))
        data[f"{prefix}_hour"] = int(request.form.get(f"{prefix}_hour", data.get(f"{prefix}_hour", 16)))
        data[f"{prefix}_minute"] = int(request.form.get(f"{prefix}_minute", data.get(f"{prefix}_minute", 0)))
        data[f"{prefix}_time_multiplier"] = int(request.form.get(f"{prefix}_time_multiplier", data.get(f"{prefix}_time_multiplier", 1)))
        data[f"{prefix}_max_wait_to_box"] = int(request.form.get(f"{prefix}_max_wait_to_box", data.get(f"{prefix}_max_wait_to_box", 10)))
        data[f"{prefix}_overtime"] = int(request.form.get(f"{prefix}_overtime", data.get(f"{prefix}_overtime", 10)))

    data["race_duration_type"] = request.form.get("race_duration_type", data.get("race_duration_type", "GameModeSelectionDuration_TIME"))
    data["min_waiting_for_players"] = int(request.form.get("min_waiting_for_players", data.get("min_waiting_for_players", 10)))
    data["max_waiting_for_players"] = int(request.form.get("max_waiting_for_players", data.get("max_waiting_for_players", 30)))

    selected_cars = request.form.getlist("selected_cars")
    cars = []

    for car_name in selected_cars:
        ballast = float(request.form.get(f"ballast_{car_name}", 0) or 0)
        restrictor = float(request.form.get(f"restrictor_{car_name}", 0) or 0)

        cars.append({
            "car_name": car_name,
            "ballast": ballast,
            "restrictor": restrictor
        })

    data["cars"] = cars

    save_server(server_id, data)

    return redirect(url(f"/server/{server_id}/settings"))




def build_generated_command(server_id, data):
    serverconfig = encode_evo_payload(build_serverconfig(data))
    seasondefinition = encode_evo_payload(build_seasondefinition(data))
    exe = server_exe_path(server_id)
    return f'"{exe}" -serverconfig {serverconfig} -seasondefinition {seasondefinition}'


def build_start_command(server_id, data):
    """Return the command line used to start the server.

    If custom_command is filled, it is used as an override.
    The user may paste either:
    - only Kunos arguments: -serverconfig ... -seasondefinition ...
    - a full command including AssettoCorsaEVOServer.exe
    """
    manual = (data.get("custom_command") or "").strip()
    manual = " ".join(manual.split())

    if manual:
        if manual.startswith("-"):
            return f'"{server_exe_path(server_id)}" {manual}'
        return manual

    return build_generated_command(server_id, data)

# ============================================================
# COMMAND
# ============================================================

@app.route("/server/<server_id>/command")
def server_command(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    data = load_server(server_id)

    generated = build_generated_command(server_id, data)
    active = build_start_command(server_id, data)

    if (data.get("custom_command") or "").strip():
        return (
            "<h3>Active command: custom Kunos command override</h3>"
            f"<pre>{active}</pre>"
            "<h3>Generated command from manager</h3>"
            f"<pre>{generated}</pre>"
        )

    return f"<pre>{generated}</pre>"


# ============================================================
# START / STOP
# ============================================================

@app.route("/server/<server_id>/start")
def start_server(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    pids = load_pids()
    old_pid = pids.get(server_id)

    if old_pid and is_pid_running(old_pid):
        if request.args.get("next") == "dash":
            return redirect(url("/dash"))
        return redirect(url(f"/server/{server_id}"))

    data = load_server(server_id)

    command_line = build_start_command(server_id, data)

    proc = subprocess.Popen(
        command_line,
        cwd=server_path(server_id),
        creationflags=CREATE_NO_WINDOW,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )

    pids[server_id] = proc.pid
    save_pids(pids)

    if request.args.get("next") == "dash":
        return redirect(url("/dash"))

    return redirect(url(f"/server/{server_id}"))


@app.route("/server/<server_id>/stop")
def stop_server(server_id):
    if not session.get("ok"):
        return redirect(url("/"))

    pids = load_pids()
    pid = pids.get(server_id)

    if pid:
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        except Exception:
            pass

    pids.pop(server_id, None)
    save_pids(pids)

    if request.args.get("next") == "dash":
        return redirect(url("/dash"))

    return redirect(url(f"/server/{server_id}"))


@app.route("/start_all")
def start_all_servers():
    if not session.get("ok"):
        return redirect(url("/"))

    pids = load_pids()

    for sid in os.listdir(SERVERS_DIR):
        if os.path.isdir(server_path(sid)) and os.path.exists(server_config_path(sid)):
            old_pid = pids.get(sid)

            if old_pid and is_pid_running(old_pid):
                continue

            data = load_server(sid)

            serverconfig = encode_evo_payload(build_serverconfig(data))
            seasondefinition = encode_evo_payload(build_seasondefinition(data))

            exe = server_exe_path(sid)

            cmd = [
                exe,
                "-serverconfig", serverconfig,
                "-seasondefinition", seasondefinition
            ]

            proc = subprocess.Popen(
                cmd,
                cwd=server_path(sid),
                creationflags=CREATE_NO_WINDOW,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )

            pids[sid] = proc.pid

    save_pids(pids)

    return redirect(url("/dash"))


@app.route("/stop_all")
def stop_all_servers():
    if not session.get("ok"):
        return redirect(url("/"))

    pids = load_pids()

    for sid, pid in list(pids.items()):
        try:
            subprocess.run(
                ["taskkill", "/PID", str(pid), "/F"],
                check=False,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                creationflags=CREATE_NO_WINDOW
            )
        except Exception:
            pass

    save_pids({})

    return redirect(url("/dash"))
