def build_serverconfig(server):
    return {
        "server_tcp_listener_port": int(server.get("tcp_port", 9700)),
        "server_udp_listener_port": int(server.get("udp_port", 9700)),
        "server_tcp_internal_port": int(server.get("tcp_port", 9700)),
        "server_udp_internal_port": int(server.get("udp_port", 9700)),
        "server_http_port": int(server.get("http_port", 8080)),
        "server_name": server.get("name", "EVO Server"),
        "max_players": int(server.get("max_players", 8)),
        "cycle": bool(server.get("cycle", True)),
        "allowed_cars_list_full": server.get("cars", []),
        "driver_password": server.get("driver_password", ""),
        "spectator_password": server.get("spectator_password", ""),
        "admin_password": server.get("admin_password", ""),
        "type": server.get("type", "MultiplayerServerListSessionType_RANKED"),
        "entry_list_path": server.get("entry_list_path", ""),
        "results_path": server.get("results_path", "")
    }


def build_seasondefinition(server):
    return {
        "game_type": server.get("game_type", "GameModeType_PRACTICE"),
        "event": {
            "track": server.get("track", "Imola"),
            "layout": server.get("layout", "GP"),
            "event_name": server.get("event_name", "GP Time Attack"),
            "track_length": str(server.get("track_length", "4909"))
        },
        "export_json": bool(server.get("export_json", False)),
        "game_config": {
            "practice_duration": int(server.get("practice_length", 3000)),
            "practice_time_of_day": {
                "year": int(server.get("year", 2024)),
                "month": int(server.get("month", 8)),
                "day": int(server.get("day", 15)),
                "hour": int(server.get("practice_hour", 16)),
                "minute": int(server.get("practice_minute", 0)),
                "second": int(server.get("second", 0)),
                "time_multiplier": int(server.get("time_multiplier", 1))
            },
            "practice_overtime_waiting_next_session": int(server.get("overtime", 10)),
            "practice_max_wait_to_box": int(server.get("max_wait_to_box", 10))
        },
        "weather_type": server.get("weather", "GameModeSelectionWeatherType_CLEAR"),
        "weather_behaviour": server.get("weather_behavior", "GameModeSelectionWeatherBehaviour_STATIC"),
        "initial_grip": server.get("initial_grip", "InitialGrip_GREEN")
    }
