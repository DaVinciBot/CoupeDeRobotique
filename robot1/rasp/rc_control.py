from config_loader import CONFIG
from brains import RemoteBrain
from loggerplusplus import Logger, LogLevels
from controllers import RollingBasis
from sensors import Lidar, LidarDummy, Inputs
from remote.remote import PS5Remote
from ws_comms import WServerRouteManager, WSender, WSreceiver, WServer


if __name__ == "__main" :
    """
    ###--- Initialization ---###
    """
    # Loggers
    # System-Part loggers
    logger_ws_server = Logger(
        identifier="WS_Server",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_route_manager = Logger(
        identifier="WS_cmd_RouteManager",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_sender = Logger(
        identifier="WS_cmd_Sender",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_receiver = Logger(
        identifier="WS_cmd_Receiver",
        follow_logger_manager_rules=True,
    )
    logger_brain = Logger(
        identifier="Brain",
        # Only Brain manages monitoring
        files_monitoring=False,
        display_monitoring=False,
        print_log_level=LogLevels.DEBUG,
        follow_logger_manager_rules=True,
    )
    logger_lidar = Logger(
        identifier="Lidar",
        follow_logger_manager_rules=True,
    )
    
    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        # ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,  # TODO: To fix, this feature is not working
    )
    # Routes
    ws_cmd = WServerRouteManager(
        logger=logger_ws_cmd_route_manager,
        receiver=WSreceiver(logger=logger_ws_cmd_receiver, use_queue=True),
        sender=WSender(logger=logger_ws_cmd_sender, name=CONFIG.WS_SENDER_NAME),
    )
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    
    lidar = LidarDummy(
        logger=logger_lidar,
        min_angle=CONFIG.LIDAR_MIN_ANGLE,
        max_angle=CONFIG.LIDAR_MAX_ANGLE,
        unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
        unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
        min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
    )
    
    # os.chdir("/home/dvb/CoupeDeRobotique/robot1/rasp")
    # Jack
    inputs = Inputs(pin_jack=CONFIG.JACK_PIN, pin_bau=CONFIG.BAU_PIN)

    
    brain = RemoteBrain(
        logger=logger_brain,
        rolling_basis=RollingBasis(),
        lidar=Lidar(
            logger=Logger(identifier="Lidar"),
            min_angle=CONFIG.LIDAR_MIN_ANGLE,
            max_angle=CONFIG.LIDAR_MAX_ANGLE,
            unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
            unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
            min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
        ),
        remote=PS5Remote(),
        ws_cmd=WServerRouteManager(
            WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
        ),
    )

    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()