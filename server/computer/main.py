from config_loader import CONFIG

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from arena import MarsArena

# from video import spawn_video_server

# Import from local path
from brains import MainBrain
from sensors import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame

import asyncio

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Loggers
    logger_ws_server = Logger(
        identifier="ws_server",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_brain = Logger(
        identifier="brain",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,
    )
    # Routes
    ws_cmd = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_pami = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    # Sensors
    ws_lidar = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_odometer = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    ws_camera = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))
    # Add routes
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    ws_server.add_route_handler(CONFIG.WS_PAMI_ROUTE, ws_pami)
    ws_server.add_route_handler(CONFIG.WS_LIDAR_ROUTE, ws_lidar)
    ws_server.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, ws_odometer)
    ws_server.add_route_handler(CONFIG.WS_CAMERA_ROUTE, ws_camera)

    # Arena
    arena = MarsArena(2, Logger(identifier="arena", print_log_level=LogLevels.INFO))

    # Brain
    brain = MainBrain(
        logger=logger_brain,
        ws_cmd=ws_cmd,
        ws_lidar=ws_lidar,
        ws_odometer=ws_odometer,
        ws_camera=ws_camera,
        ws_pami=ws_pami,
        arena=arena,
        config=CONFIG,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
