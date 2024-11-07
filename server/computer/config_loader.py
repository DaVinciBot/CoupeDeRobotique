import numpy as np
import pathlib
import json
import sys
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except Exception as error:
        print(f"Error while loading the file {file_path}: {error}")
        raise error

    return file_json


def format_path(path: str) -> str:
    """
    Transform a path with this shape: '.|folder|sub_folder|file.txt'
    to the path with the correct separator  ('\' for Windows or '/' for Unix-based systems),
    depending on the operating system.
    """
    try:
        path_parts = path.split("|")
        return os.path.join(*path_parts)
    except Exception as error:
        print(f"Error while formatting the path {path}: {error}")
        raise error


class CONFIG:
    # TO CONFIG !
    RELATIVE_ROOT_PATH = os.path.join("..", "..")
    SPECIFIC_CONFIG_KEY = "computer"
    GENERAL_CONFIG_KEY = "general"

    # Directory path (dont't touch)
    ROOT_DIR = os.path.abspath(RELATIVE_ROOT_PATH)
    BASE_DIR = pathlib.Path(__file__).resolve().parent
    COMMON_DIR = os.path.join(ROOT_DIR, "common")
    sys.path.append(
        COMMON_DIR
    )  # Add common directory to the path (to be able to import common modules)
    CONFIG_STORE = load_json_file(os.path.join(ROOT_DIR, "config.json"))

    # CONSTANTS TO DEFINE !
    # General config
    GENERAL_CONFIG = CONFIG_STORE[GENERAL_CONFIG_KEY]
    GENERAL_WS_CONFIG = GENERAL_CONFIG["ws"]

    WS_PORT = int(GENERAL_WS_CONFIG["port"])
    WS_LIDAR_ROUTE = GENERAL_WS_CONFIG["lidar_route"]
    WS_LOG_ROUTE = GENERAL_WS_CONFIG["log_route"]
    WS_CAMERA_ROUTE = GENERAL_WS_CONFIG["camera_route"]
    WS_ODOMETER_ROUTE = GENERAL_WS_CONFIG["odometer_route"]
    WS_CMD_ROUTE = GENERAL_WS_CONFIG["cmd_route"]
    WS_PAMI_ROUTE = GENERAL_WS_CONFIG["pami_route"]

    # Specific config
    SPECIFIC_CONFIG = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])

    # Specific camera config
    SPECIFIC_CAMERA_CONFIG = SPECIFIC_CONFIG["camera"]

    CAMERA_RESOLUTION = SPECIFIC_CAMERA_CONFIG["resolution"]
    CAMERA_CHESSBOARD_SIZE = SPECIFIC_CAMERA_CONFIG["chessboard_size"]
    CAMERA_CHESSBOARD_SQUARE_SIZE = float(
        SPECIFIC_CAMERA_CONFIG["chessboard_square_size"]
    )
    CAMERA_DISTANCE_CAM_TABLE = float(SPECIFIC_CAMERA_CONFIG["distance_cam_table"])
    CAMERA_SAVE_PATH = format_path(SPECIFIC_CAMERA_CONFIG["save_path"])
    CAMERA_CALIBRATION_PATH = format_path(SPECIFIC_CAMERA_CONFIG["calibration_path"])
    CAMERA_COEFFICIENTS_PATH = format_path(SPECIFIC_CAMERA_CONFIG["coefficients_path"])

    CAMERA_CAM_OBJ_FUNCTION_A = float(
        SPECIFIC_CAMERA_CONFIG["aruco"]["cam_obj_function_a"]
    )
    CAMERA_CAM_OBJ_FUNCTION_B = float(
        SPECIFIC_CAMERA_CONFIG["aruco"]["cam_obj_function_b"]
    )
    CAMERA_ARUCO_DICT_TYPE = SPECIFIC_CAMERA_CONFIG["aruco"]["aruco_dict_type"]

    CAMERA_COLOR_FILTER_NAME = SPECIFIC_CAMERA_CONFIG["color_object"]["color"]
    CAMERA_COLOR_FILTER_RANGE = (
        np.array(SPECIFIC_CAMERA_CONFIG["color_object"]["hsv_min"]),
        np.array(SPECIFIC_CAMERA_CONFIG["color_object"]["hsv_max"]),
    )
    CAMERA_COLOR_CLUSTERING_EPS = int(
        SPECIFIC_CAMERA_CONFIG["color_object"]["clustering_eps"]
    )
    CAMERA_COLOR_CLUSTERING_MIN_SAMPLES = int(
        SPECIFIC_CAMERA_CONFIG["color_object"]["clustering_min_samples"]
    )

    CAMERA_PICKUP_ZONE_MIN_AREA = int(
        SPECIFIC_CAMERA_CONFIG["camera_pickup_zone_min_area"]
    )
