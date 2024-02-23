# TODO: Constants for the server, it has to be in a config file !
HOSTNAME = "localhost"
PORT = 8080
SENDER_NAME = "server"

import sys
from pathlib import Path

current_dir = Path(__file__).parent.parent
sys.path.append(str(current_dir.parent / 'common'))

from common.WS import (
    WServer, WServerRouteManager,
    WSender, WSreceiver,
    WSmsg
)


if __name__ == "__main__":
    ws_server = WServer(HOSTNAME, PORT)

    # Lidar
    lidar = WServerRouteManager(
        WSreceiver(keep_memory=True),
        WSender(SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(use_queue=True),
        WSender(SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(keep_memory=True),
        WSender(SENDER_NAME)
    )

    # Bind routes
    ws_server.add_route_handler("/lidar", lidar)
    ws_server.add_route_handler("/log", log)
    ws_server.add_route_handler("/odometer", odometer)

    # Add background tasks
    ws_server.add_background_task(lidar_brain)

    ws_server.run()
