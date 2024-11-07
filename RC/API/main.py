from API import API, handle_lidar_ws, handle_log_ws, handle_cmd_ws, handle_state_ws


SERVER = {
    "lidar": {"connections": set(), "handler": handle_lidar_ws},
    "log": {"connections": set(), "handler": handle_log_ws},
    "cmd": {"connections": set(), "handler": handle_cmd_ws},
    "state": {"connections": set(), "handler": handle_state_ws},
}


def main():
    api = API(SERVER)
    api.run()


if __name__ == "__main__":
    main()
