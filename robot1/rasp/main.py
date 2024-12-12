from config_loader import CONFIG

import math

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from geometry import OrientedPoint
from led_strip import LEDStrip
from arena import MarsArena
from GPIO import PIN

# Import from local path
from brains import MainBrain
from controllers import RollingBasis, Actuators
from sensors import Lidar

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
    logger_rolling_basis = Logger(
        identifier="rolling_basis",
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

    # Robot
    rolling_basis = RollingBasis(logger=logger_rolling_basis)

    # Brain
    brain = MainBrain(logger=logger_brain, rolling_basis=rolling_basis)

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_tasks():
        ws_server.add_background_task(routine)

    ws_server.run()
