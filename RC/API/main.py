from API import API, handle_lidar_ws, handle_log_ws, handle_cmd_ws

CONNECTIONS_LIDAR = set()
CONNECTIONS_LOG = set()
CONNECTIONS_STATE = set()
CONNECTIONS_CMD = set()


SERVER = {
    "lidar": {"connections": CONNECTIONS_LIDAR, "handler": handle_lidar_ws},
    "log": {"connections": CONNECTIONS_LOG, "handler": handle_log_ws},
    "cmd": {"connections": CONNECTIONS_CMD, "handler": handle_cmd_ws},
    # "state": {"connections": CONNECTIONS_STATE},
}


def main():
    api = API(SERVER)
    api.run()


if __name__ == "__main__":
    main()
