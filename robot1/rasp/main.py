# ====== Imports ======
# Config
from config_loader import CONFIG

# Logger: LoggerManager + global configuration
from loggerplusplus import LoggerManager, LogLevels, LoggerConfig, Logger, logger_colors

LoggerManager.enable_files_logs_monitoring_only_for_one_logger = True
# LoggerManager.enable_dynamic_config_update = False
# LoggerManager.enable_unique_logger_identifier = False
LoggerManager.global_config = LoggerConfig.from_kwargs(
    colors=logger_colors.ClassicColors,
    path="logs",
    # LogLevels
    decorator_log_level=LogLevels.DEBUG,
    print_log_level=LogLevels.INFO,
    file_log_level=LogLevels.DEBUG,
    # Loggers Output
    print_log=True,
    write_to_file=True,
    # Monitoring
    display_monitoring=False,
    files_monitoring=False,
    file_size_unit="Go",
    disk_alert_threshold_percent=0.8,
    log_files_size_alert_threshold_percent=0.2,
    max_log_file_size=1.0,
    # Placement
    identifier_max_width=15,
    filename_lineno_max_width=15,
)

# Internal project imports
from ws_comms import WServer, WServerRouteManager, WSender, WSreceiver
from arena import ShowArena
from geometry import OrientedPoint
from brains import MainBrain
from controllers import RollingBasisDummy, RollingBasis
from movement_manager import MovementManager
from sensors import LidarDummy, Lidar

# ====== Main ======
if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Loggers
    # System-Part loggers
    logger_ws_server = Logger(
        identifier="WS_Server",
        follow_logger_manager_rules=True,
    )
    logger_brain = Logger(
        identifier="Brain",
        # Only Brain manages monitoring
        files_monitoring=True,
        display_monitoring=True,
        follow_logger_manager_rules=True,
    )

    # Controllers loggers
    logger_rolling_basis = Logger(
        identifier="RollingBasis",
        follow_logger_manager_rules=True,
    )
    # Sensors loggers
    logger_lidar = Logger(
        identifier="LiDAR",
        follow_logger_manager_rules=True,
    )
    # Environment loggers
    logger_grid_manager = Logger(
        identifier="GridManager",
        follow_logger_manager_rules=True,
    )
    logger_show_arena = Logger(
        identifier="ShowArena",
        follow_logger_manager_rules=True,
    )
    # Movement loggers
    logger_rolling_basis_handler = Logger(
        identifier="RollingBasisHandler",
        follow_logger_manager_rules=True,
    )
    logger_path_finder = Logger(
        identifier="PathFinder",
        follow_logger_manager_rules=True,
    )
    logger_movement_manager = Logger(
        identifier="MovementManager",
        follow_logger_manager_rules=True,
    )

    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,  # TODO: je crois que ça marche pas cette feature
    )
    # Routes
    ws_cmd = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)

    # Controllers
    # Rolling Basis
    rolling_basis = RollingBasis(logger=logger_rolling_basis)
    # rolling_basis = RollingBasisDummy(logger=logger_rolling_basis)

    rolling_basis.set_odometrie(OrientedPoint(50, 80, 0))
    # rolling_basis.set_pids(
    #     0, 0, 0,
    #     0, 0, 0,
    #     0, 0, 0,
    #     0, 0, 0
    # )

    # Sensors
    # Lidar
    # lidar = Lidar(
    #     logger=logger_lidar,
    #     min_angle=CONFIG.LIDAR_MIN_ANGLE,
    #     max_angle=CONFIG.LIDAR_MAX_ANGLE,
    #     unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
    #     unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
    #     min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
    # )
    lidar = LidarDummy(
        logger=logger_lidar,
        min_angle=CONFIG.LIDAR_MIN_ANGLE,
        max_angle=CONFIG.LIDAR_MAX_ANGLE,
        unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
        unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
        min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
    )

    # Environment
    # Arena
    arena = ShowArena(
        logger=logger_show_arena,
        border_buffer=2,
        obstacle_buffer=1,
        chunk_size=5,
        forbidden_cover_threshold=0.1,
        grid_manager_logger=logger_grid_manager,
    )

    # Movement
    # Movement Manager
    movement_manager = MovementManager(
        logger=logger_movement_manager,
        rolling_basis_handler_logger=logger_rolling_basis_handler,
        path_finder_logger=logger_path_finder,
        movement_resolution=1,
        arena=arena,
    )

    # Brain
    brain = MainBrain(
        logger=logger_brain,
        rolling_basis=rolling_basis,
        lidar=lidar,
        arena=arena,
        movement_manager=movement_manager,
        ws_cmd=ws_cmd,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
