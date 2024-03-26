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
    """
    ###--- Initialization ---###
    """
    # Logger
    logger = Logger(
        identifier="robot1",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_client = WSclient(CONFIG.WS_SERVER_IP, CONFIG.WS_PORT)
    ws_cmd = WSclientRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_log = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    # Sensors
    ws_lidar = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_odometer = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_camera = WSclientRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    ws_client.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    ws_client.add_route_handler(CONFIG.WS_LOG_ROUTE, ws_log)

    ws_client.add_route_handler(CONFIG.WS_LIDAR_ROUTE, ws_lidar)
    ws_client.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, ws_odometer)
    ws_client.add_route_handler(CONFIG.WS_CAMERA_ROUTE, ws_camera)

    # Robot
    robot = RollingBasis(logger=logger)
    robot.set_home(0.0, 0.0, 0.0)

    # Lidar
    lidar = Lidar()

    # Arene
    #arena = MarsArena(1)

    # Brain
    brain = Robot1Brain(
        logger=logger,
        ws_cmd=ws_cmd,
        ws_log=ws_log,
        ws_lidar=ws_lidar,
        ws_odometer=ws_odometer,
        ws_camera=ws_camera,
        rolling_basis=robot,
        lidar=lidar,
        #arena=arena,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_client.add_background_task(routine)

    ws_client.run()
