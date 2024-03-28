from config_loader import CONFIG

# Import from common
from logger import Logger, LogLevels
from geometry import OrientedPoint
from arena import MarsArena
from WS_comms import WSclient, WSclientRouteManager, WSender, WSreceiver, WSmsg

# Import from local path
from sensors import Lidar
from controllers import RollingBasis, Actuators
from brains import Robot1Brain

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Loggers
    logger_ws_client = Logger(
        identifier="ws_client",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_brain = Logger(
        identifier="brain",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_rolling_basis = Logger(
        identifier="rolling_basis",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_actuators = Logger(
        identifier="actuators",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )
    logger_arena = Logger(
        identifier="arena",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.INFO,
        file_log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_client = WSclient(CONFIG.WS_SERVER_IP, CONFIG.WS_PORT, logger=logger_ws_client)
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
    rolling_basis = RollingBasis(logger=logger_rolling_basis)

    actuators = Actuators(logger=logger_actuators)

    # Lidar
    lidar = Lidar()

    start_zone_id = 2

    # Arena
    arena = MarsArena(
        start_zone_id, logger=logger_arena
    )  # must be declared from external calculus interface or switch on the robot

    start_pos = OrientedPoint.from_Point(arena.zones["home"].centroid)
    rolling_basis.set_home(start_pos)

    # Brain
    brain = Robot1Brain(
        actuators=actuators,
        logger=logger_brain,
        ws_cmd=ws_cmd,
        ws_log=ws_log,
        ws_lidar=ws_lidar,
        ws_odometer=ws_odometer,
        ws_camera=ws_camera,
        rolling_basis=rolling_basis,
        lidar=lidar,
        arena=arena,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_client.add_background_task(routine)

    ws_client.run()
