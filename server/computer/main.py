from config_loader import CONFIG

# Import from common
from WS_comms import WServer, WServerRouteManager, WSender, WSreceiver, WSmsg
from logger import Logger, LogLevels
from arena import MarsArena

# Import from local path
from brains import ServerBrain
from controllers import Camera, ArucoRecognizer, ColorRecognizer, PlanTransposer, Frame

import asyncio

if __name__ == "__main__":
    """
    ###--- Initialization ---###
    """
    # Logger
    logger = Logger(
        identifier="computer",
        dec_level=LogLevels.INFO,
        log_level=LogLevels.DEBUG,
    )

    # Websocket server
    ws_server = WServer(CONFIG.WS_HOSTNAME, CONFIG.WS_PORT)
    ws_lidar = WServerRouteManager(
        WSreceiver(keep_memory=True, use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_odometer = WServerRouteManager(
        WSreceiver(keep_memory=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_cmd = WServerRouteManager(
        WSreceiver(use_queue=True), WSender(CONFIG.WS_SENDER_NAME)
    )
    ws_log = WServerRouteManager(WSreceiver(), WSender(CONFIG.WS_SENDER_NAME))

    ws_server.add_route_handler(CONFIG.WS_LIDAR_ROUTE, ws_lidar)
    ws_server.add_route_handler(CONFIG.WS_ODOMETER_ROUTE, ws_odometer)
    ws_server.add_route_handler(CONFIG.WS_CMD_ROUTE, ws_cmd)
    ws_server.add_route_handler(CONFIG.WS_LOG_ROUTE, ws_log)

    # Camera
    camera = Camera(
        res_w=CONFIG.CAMERA_RESOLUTION[0],
        res_h=CONFIG.CAMERA_RESOLUTION[1],
        captures_path=CONFIG.CAMERA_SAVE_PATH,
        undistorted_coefficients_path=CONFIG.CAMERA_COEFFICIENTS_PATH,
    )

    aruco_recognizer = ArucoRecognizer(aruco_type=CONFIG.CAMERA_ARUCO_DICT_TYPE)

    color_recognizer = ColorRecognizer(
        detection_range=CONFIG.CAMERA_COLOR_FILTER_RANGE,
        name=CONFIG.CAMERA_COLOR_FILTER_NAME,
        clustering_eps=CONFIG.CAMERA_COLOR_CLUSTERING_EPS,
        clustering_min_samples=CONFIG.CAMERA_COLOR_CLUSTERING_MIN_SAMPLES,
    )

    plan_transposer = PlanTransposer(
        camera_table_distance=CONFIG.CAMERA_DISTANCE_CAM_TABLE,
        alpha=CONFIG.CAMERA_CAM_OBJ_FUNCTION_A,
        beta=CONFIG.CAMERA_CAM_OBJ_FUNCTION_B,
    )
    camera.load_undistor_coefficients()

    # Arena
    arena = MarsArena(1)

    # Brain
    brain = ServerBrain(
        logger=logger,
        ws_lidar=ws_lidar,
        ws_odometer=ws_odometer,
        ws_cmd=ws_cmd,
        ws_log=ws_log,
        camera=camera,
        aruco_recognizer=aruco_recognizer,
        color_recognizer=color_recognizer,
        plan_transposer=plan_transposer,
        arena=arena,
    )

    """
        ###--- Run ---###
    """
    # Add background tasks, in format ws_server.add_background_task(func, func_params)
    for routine in brain.get_routines():
        ws_server.add_background_task(routine)

    ws_server.run()
