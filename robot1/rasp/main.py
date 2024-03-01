from config_loader import CONFIG

# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg

# Import from local path
from sensors import Lidar
from controllers import RollingBasis
from brains import Robot1Brain

import asyncio


if __name__ == "__main__":
    # Logger
    logger = Logger(
        identifier="robot1",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )

    # Arene
    arena = MarsArena(1)

    # Robot
    robot = RollingBasis()
    lidar_obj = Lidar()

    # WS connection
    ws_client = WSclient(CONFIG.WS_SERVER_IP, CONFIG.WS_PORT)

    # Lidar
    lidar = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Log
    cmd = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    # Odometer
    odometer = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    
    # Brain
    brain = Robot1Brain(logger, arena, lidar_obj, robot, lidar, odometer, cmd)

    # Bind routes
    ws_client.add_route_handler(CONFIG.WS_LIDAR_ROUTE, lidar)
    ws_client.add_route_handler(CONFIG.WS_CMD_ROUTE, cmd)
    ws_client.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, odometer)

    # Add background tasks
    ws_client.add_background_task(brain.routine)

    
    ws_client.run()
