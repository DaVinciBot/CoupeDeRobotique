from config_loader import CONFIG

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from arena import MarsArena

# Import from local path
from brains import ServerBrain

import asyncio


if __name__ == "__main__":
    logger = Logger(
        identifier="computer",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )
    ws_server = WServer(CONFIG.WS_HOSTNAME, CONFIG.WS_PORT)

    # Arene
    arene = MarsArena(1)
    
    # Lidar
    lidar = WServerRouteManager(
        WSreceiver(keep_memory=True, use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Log
    log = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Odometer
    odometer = WServerRouteManager(
        WSreceiver(keep_memory=True), WSender(CONFIG.WS_SENDER_NAME)
    )

    # Cmd
    cmd = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Brain
    brain = ServerBrain(logger, arene, lidar, odometer, cmd)
    
    # Bind routes
    ws_server.add_route_handler(CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_server.add_route_handler(CONFIG.WS_LOG_ROUTE, log)
    ws_server.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, odometer)
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, cmd)

    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    ws_server.add_background_task(brain.routine)

    ws_server.run()
