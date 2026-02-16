"""Main entry point to run the Boombot demo on the Raspberry Pi."""

from __future__ import annotations

import subprocess
import sys

from loggerplusplus import LogLevels
from taskbrain import DictProxyAccessor
from ws_comms import WSender, WServer, WServerRouteManager, WSreceiver

from a_config_loader import CONFIG
from arena.base_arena.arena_zones import AllyZone
from arena.winter_arena import WinterArena
from brains import MainBrain
from geometry import OrientedPoint
from log_manager import LogLogger
from navigation.navigator.task import NavigatorTaskParams
from sensors import Inputs, Lidar, LidarDummy

_logger = LogLogger(
    identifier="Main",
    follow_logger_manager_rules=True,
)

# ====== Main ======
if __name__ == "__main__":
    _logger.info("[INIT] Initializing all systems...")
    # region ====== Initialization ======

    # Loggers
    # System-Part loggers
    logger_ws_server = LogLogger(
        identifier="WS_Server",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_route_manager = LogLogger(
        identifier="WS_cmd_RouteManager",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_sender = LogLogger(
        identifier="WS_cmd_Sender",
        follow_logger_manager_rules=True,
    )
    logger_ws_cmd_receiver = LogLogger(
        identifier="WS_cmd_Receiver",
        follow_logger_manager_rules=True,
    )

    logger_ws_ui_route_manager = LogLogger(
        identifier="WS_UI_RouteManager",
        follow_logger_manager_rules=True,
    )
    logger_ws_ui_sender = LogLogger(
        identifier="WS_UI_Sender",
        follow_logger_manager_rules=True,
    )
    logger_ws_ui_receiver = LogLogger(
        identifier="WS_UI_Receiver",
        follow_logger_manager_rules=True,
    )

    logger_brain = LogLogger(
        identifier="Brain",
        # Only Brain manages monitoring
        files_monitoring=False,
        display_monitoring=False,
        print_log_level=LogLevels.DEBUG,
        follow_logger_manager_rules=True,
    )
    logger_lidar = LogLogger(
        identifier="Lidar",
        follow_logger_manager_rules=True,
    )

    # Controllers loggers
    # See ./brains/controllers_brain.py for more details
    # All rolling basis part is executed in another process so define inside this part

    # Environment loggers
    logger_grid_manager = LogLogger(
        identifier="GridManager",
        print_log_level=LogLevels.INFO,
        follow_logger_manager_rules=True,
    )
    logger_show_arena = LogLogger(
        identifier="ShowArena",
        follow_logger_manager_rules=True,
    )

    # Movement loggers
    # See ./brains/controllers_brain.py for more details
    # All rolling basis part is executed in another process so define inside this part
    """ Main object instances """
    # Websocket server
    # Websocket server
    ws_server = WServer(
        logger=logger_ws_server,
        host=CONFIG.WS_HOSTNAME,
        port=CONFIG.WS_PORT,
        # ping_pong_clients_interval=CONFIG.WS_PING_PONG_INTERVAL,
        # TODO: To fix, this feature is not working
    )
    # Routes
    ws_cmd = WServerRouteManager(
        logger=logger_ws_cmd_route_manager,
        receiver=WSreceiver(logger=logger_ws_cmd_receiver, use_queue=True),
        sender=WSender(logger=logger_ws_cmd_sender, name=CONFIG.WS_SENDER_NAME),
    )
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)

    ws_ui = WServerRouteManager(
        logger=logger_ws_ui_route_manager,
        receiver=WSreceiver(logger=logger_ws_ui_receiver, use_queue=True),
        sender=WSender(logger=logger_ws_ui_sender, name=CONFIG.WS_UI_SENDER_NAME),
    )
    ws_server.add_route_handler(CONFIG.WS_UI_ROUTE, ws_ui)

    # Controllers
    # Rolling Basis
    # See ./brains/controllers_brain.py for more details
    # All rolling basis part is executed in another process so define inside this part

    # Sensors
    # Lidar
    if CONFIG.LIDAR_DUMMY:
        lidar: Lidar | LidarDummy = LidarDummy(
            logger=logger_lidar,
            min_angle=CONFIG.LIDAR_MIN_ANGLE,
            max_angle=CONFIG.LIDAR_MAX_ANGLE,
            unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
            unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
            min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
        )
    else:
        lidar = Lidar(
            logger=logger_lidar,
            min_angle=CONFIG.LIDAR_MIN_ANGLE,
            max_angle=CONFIG.LIDAR_MAX_ANGLE,
            unit_angle=CONFIG.LIDAR_ANGLES_UNIT,
            unit_distance=CONFIG.LIDAR_DISTANCES_UNIT,
            min_distance=CONFIG.LIDAR_MIN_DISTANCE_DETECTION,
        )

    # Environment
    # Arena
    arena = WinterArena(
        logger=logger_show_arena,
        border_buffer=CONFIG.ARENA_BORDER_BUFFER,
        obstacle_buffer=CONFIG.ARENA_OBSTACLE_BUFFER,
        chunk_size=CONFIG.ARENA_CHUNK_SIZE,
        forbidden_cover_threshold=CONFIG.ARENA_FORBIDDEN_COVER_THRESHOLD,
        grid_manager_logger=logger_grid_manager,
    )

    # os.chdir("/home/dvb/CoupeDeRobotique/robot1/rasp")
    # Jack
    inputs = Inputs(pin_jack=CONFIG.JACK_PIN, pin_bau=CONFIG.BAU_PIN)

    # Movement
    # Movement manager
    # See ./brains/controllers_brain.py for more details
    # All rolling basis part is executed in another process so define inside this part

    # Brain
    # Register object types that must be shared between processes
    DictProxyAccessor.add_serializable_type(WinterArena, arena)
    DictProxyAccessor.add_serializable_type(OrientedPoint)
    DictProxyAccessor.add_serializable_type(NavigatorTaskParams)
    DictProxyAccessor.add_serializable_type(AllyZone)

    brain = MainBrain(
        logger=logger_brain,
        lidar=lidar,
        arena=arena,
        ws_cmd=ws_cmd,
        ws_ui=ws_ui,
        inputs=inputs,
    )

    # endregion

    # region ====== Run ======

    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    def force_kill_all_python() -> None:
        """Kill all running Python processes using pkill -9 python."""
        subprocess.run(["pkill", "-9", "python"], check=False)  # noqa: S607
        logger_brain.fatal("[SHUTDOWN] All Python processes killed.")

    logger_brain.info("[INIT] All systems initialized successfully")
    logger_brain.info("[INIT] Starting WebSocket server...")

    args_launch = sys.argv
    if "-i" in args_launch:
        logger_brain.info("Opening iihm...")
        try:
            subprocess.Popen([
                "chromium",
                "--no-sandbox",
                "/home/dvb/CoupeDeRobotique/robot1/rasp/WebUI/index.html",
            ])
        except FileNotFoundError:
            logger_brain.warning("Chromium not found.")

    ws_server.add_shutdown_task(force_kill_all_python)
    ws_server.run()

    # endregion
