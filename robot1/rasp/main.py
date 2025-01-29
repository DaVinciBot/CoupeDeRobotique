from config_loader import CONFIG

import math

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from arena import ShowArena

# Import from local path
from brains import MainBrain
from controllers import RollingBasis, RollingBasisDummy
from movement_manager import MovementManager
from sensors import LidarDummy, Lidar
from remote import PS5Remote

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Loggers
    # System-Part loggers
    logger_ws_server = Logger(
        identifier="WS_Server",
        decorator_level=LogLevels.INFO,
        print_log_level=LogLevels.DEBUG,
        file_log_level=LogLevels.DEBUG,
    )
    logger_brain = Logger(
        identifier="Brain",
    )
    # Controllers loggers
    logger_rolling_basis = Logger(
        identifier="RollingBasis",
    )
    # Sensors loggers
    logger_lidar = Logger(
        identifier="LiDAR",
    )
    # Environment loggers
    logger_grid_manager = Logger(
        identifier="GridManager",
    )
    logger_show_arena = Logger(
        identifier="ShowArena",
    )
    # Movement loggers
    logger_rolling_basis_handler = Logger(
        identifier="RollingBasisHandler",
    )
    logger_path_finder = Logger(
        identifier="PathFinder",
    )
    logger_movement_manager = Logger(
        identifier="MovementManager",
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
    # rolling_basis = RollingBasis(logger=logger_rolling_basis)
    rolling_basis = RollingBasisDummy(logger=logger_rolling_basis)

    # Sensors
    # Lidar
    # lidar = Lidar(logger=logger_lidar)
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
    brain.activate()
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
