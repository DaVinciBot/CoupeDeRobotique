import json
import os
import pathlib
import sys


def load_json_file(file_path: str) -> dict:
    """Load a JSON file and return its content.

    Args:
        file_path (str): The path to the JSON file.

    Returns:
        dict: The content of the JSON file as a dictionary.

    Raises:
        Exception: If the file cannot be read or parsed.
    """
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except Exception:
        raise

    return file_json


class CONFIG:
    """Configuration class to load and store configuration settings.

    Attributes:
        ROOT_DIR (pathlib.Path): The root directory of the project.
        COMMON_DIR (pathlib.Path): The path to the common directory.
        CONFIG_STORE (dict): The loaded configuration from config.json.

        GENERAL_CONFIG_KEY (str): Key for general configuration in the config file.
        SPECIFIC_CONFIG_KEY (str): Key for specific configuration in the config file.
        ARENA_CONFIG_KEY (str): Key for arena configuration in the config file.

        GENERAL_CONFIG (dict): General configuration settings.
        GENERAL_WS_CONFIG (dict): WebSocket configuration settings.
        GENERAL_TEENSY_CONFIG (dict): Teensy configuration settings.

        WS_PORT (int): WebSocket port.
        WS_CMD_ROUTE (str): WebSocket command route.
        TEENSY_VID (int): Teensy USB vendor ID.
        TEENSY_PID (int): Teensy USB product ID.
        TEENSY_BAUDRATE (int): Baud rate for Teensy communication.
        TEENSY_CRC (bool): Whether to enable CRC for Teensy communication.
        TEENSY_DUMMY (bool): Whether to enable dummy mode for Teensy communication.

        SPECIFIC_CONFIG (dict): Specific configuration settings for the robot.
        SPECIFIC_WS_CONFIG (dict): Specific WebSocket configuration settings.

        WS_SENDER_NAME (str): WebSocket sender name.
        WS_HOSTNAME (str): WebSocket hostname.
        WS_PING_PONG_INTERVAL (int): WebSocket ping-pong interval in seconds.

        ZOMBIE_MODE (bool): Whether the robot is in zombie mode.

        LOG_CONFIG (dict): Logging configuration settings.
        LOGGER_MANAGER_CONFIG (dict): Logger manager configuration settings.
        LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER (bool): Whether to enable file logs monitoring for one logger only.
        LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE (bool): Whether to enable dynamic config update for the logger
        LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER (bool): Whether to enable unique logger identifier.

        LOGGER_CONFIG (dict): Logger configuration settings.
        LOGGER_COLORS (str): Logger colors configuration.
        LOGGER_PATH (str): Path for logger files.
        LOGGER_DECORATOR_LOG_LEVEL (str): Log level for decorator logs.
        LOGGER_PRINT_LOG_LEVEL (str): Log level for printed logs.
        LOGGER_FILE_LOG_LEVEL (str): Log level for file logs.
        LOGGER_PRINT_LOG (bool): Whether to print logs to console.
        LOGGER_WRITE_TO_FILE (bool): Whether to write logs to file.
        LOGGER_DISPLAY_MONITORING (bool): Whether to display monitoring information.
        LOGGER_FILES_MONITORING (bool): Whether to monitor log files.
        LOGGER_FILE_SIZE_UNIT (str): Unit for file size in logs.
        LOGGER_DISK_ALERT_THRESHOLD_PERCENT (float): Disk alert threshold percentage.
        LOGGER_FILES_SIZE_ALERT_THRESHOLD_PERCENT (float): Log files size alert threshold percentage.
        LOGGER_MAX_LOG_FILE_SIZE (float): Maximum size for log files.
        LOGGER_IDENTIFIER_MAX_WIDTH (float): Maximum width for logger identifier.
        LOGGER_FILENAME_LINENO_MAX_WIDTH (float): Maximum width for filename and line number in logs.

        TEAM_CONFIG (dict): Team configuration settings.
        DEFAULT_TEAM (str): Default team color.
        INFO_BY_TEAM (dict): Information by team.

        ROLLING_BASIS_CONFIG (dict): Rolling basis configuration settings.
        ROLLING_BASIS_TEENSY_SER (int): Serial number for the rolling basis Teensy.
        ROLLING_BASIS_PIDS_CONFIG (dict): PID configuration for the rolling basis.
        ROLLING_BASIS_PIDS_LINEAR_SPEED (dict): PID settings for linear speed
        ROLLING_BASIS_PIDS_ANGULAR_SPEED (dict): PID settings for angular speed.
        ROLLING_BASIS_PIDS_LINEAR_POSITION (dict): PID settings for linear position
        ROLLING_BASIS_PIDS_ANGULAR_POSITION (dict): PID settings for angular position.

        ROLLING_BASIS_SPEED_PROFILES_CONFIG (dict): Speed profiles configuration for the rolling basis.
        ROLLING_BASIS_DEFAULT_SPEED_PROFILE (dict): Default speed profile settings.
        ROLLING_BASIS_HIGH_SPEED_PROFILE (dict): High speed profile settings.

        ACTUATORS_CONFIG (dict): Actuators configuration settings.
        ACTUATOR_TEENSY_SER (int): Serial number for the actuators Teensy

        LIDAR_CONFIG (dict): Lidar configuration settings.
        LIDAR_ANGLES_UNIT (str): Unit for lidar angles.
        LIDAR_DISTANCES_UNIT (str): Unit for lidar distances.
        LIDAR_MIN_ANGLE (float): Minimum angle for lidar detection.
        LIDAR_MAX_ANGLE (float): Maximum angle for lidar detection.
        LIDAR_MIN_DISTANCE_DETECTION (float): Minimum distance for lidar detection.
        LIDAR_FRONTAL_DETECTION_ANGLE (float): Frontal detection angle for lidar
        LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE (float): Semi-circular detection angle for lidar.

        ARENA_CONFIG (dict): Arena configuration settings.
        ARENA_BORDER_BUFFER (float): Buffer size for arena borders.
        ARENA_OBSTACLE_BUFFER (float): Buffer size for arena obstacles.
        ARENA_CHUNK_SIZE (float): Size of the arena chunks.
        ARENA_FORBIDDEN_COVER_THRESHOLD (float): Threshold for forbidden cover in the arena.
    """

    # Directory path (dont't touch)
    ROOT_DIR: pathlib.Path = (
        pathlib.Path(__file__).resolve().parent.parent.parent.parent
    )

    COMMON_DIR: pathlib.Path = os.path.join(ROOT_DIR, "common")
    sys.path.append(
        COMMON_DIR,
    )  # Add common directory to the path (to be able to import common modules)
    CONFIG_STORE: dict = load_json_file(os.path.join(ROOT_DIR, "config.json"))

    # TO CONFIG !
    GENERAL_CONFIG_KEY: str = "general"
    SPECIFIC_CONFIG_KEY: str = "rob"
    ARENA_CONFIG_KEY: str = "arena"

    # CONSTANTS TO DEFINE !
    # General config
    GENERAL_CONFIG: dict = CONFIG_STORE[GENERAL_CONFIG_KEY]
    GENERAL_WS_CONFIG: dict = GENERAL_CONFIG["ws"]
    GENERAL_TEENSY_CONFIG: dict = GENERAL_CONFIG["teensy"]

    WS_PORT: int = int(GENERAL_WS_CONFIG["port"])
    WS_CMD_ROUTE: str = GENERAL_WS_CONFIG["cmd_route"]

    TEENSY_VID: int = GENERAL_TEENSY_CONFIG["vid"]
    TEENSY_PID: int = GENERAL_TEENSY_CONFIG["pid"]
    TEENSY_BAUDRATE: int = GENERAL_TEENSY_CONFIG["baudrate"]
    TEENSY_CRC: bool = GENERAL_TEENSY_CONFIG["crc"]
    TEENSY_DUMMY: bool = GENERAL_TEENSY_CONFIG["dummy"]

    # Specific config
    SPECIFIC_CONFIG: dict = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG: dict = SPECIFIC_CONFIG["ws"]

    WS_SENDER_NAME: str = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME: str = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL: int = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])

    # Zombie mode
    ZOMBIE_MODE: bool = SPECIFIC_CONFIG["zombie_mode"]
    if "-z" in sys.argv or "--zombie" in sys.argv:
        ZOMBIE_MODE = True
    if "-g" in sys.argv or "--game" in sys.argv:
        ZOMBIE_MODE = False

    # Logs
    LOG_CONFIG: dict = SPECIFIC_CONFIG["log"]

    LOGGER_MANAGER_CONFIG: dict = LOG_CONFIG["logger_manager"]
    LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER: bool = (
        LOGGER_MANAGER_CONFIG["enable_files_logs_monitoring_only_for_one_logger"]
    )
    LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE: bool = LOGGER_MANAGER_CONFIG[
        "enable_dynamic_config_update"
    ]
    LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER: bool = LOGGER_MANAGER_CONFIG[
        "enable_unique_logger_identifier"
    ]

    LOGGER_CONFIG: dict = LOG_CONFIG["logger"]
    LOGGER_COLORS: str = LOGGER_CONFIG["colors"]
    LOGGER_PATH: str = LOGGER_CONFIG["path"]
    LOGGER_DECORATOR_LOG_LEVEL: str = LOGGER_CONFIG["decorator_log_level"]
    LOGGER_PRINT_LOG_LEVEL: str = LOGGER_CONFIG["print_log_level"]
    LOGGER_FILE_LOG_LEVEL: str = LOGGER_CONFIG["file_log_level"]
    LOGGER_PRINT_LOG: bool = LOGGER_CONFIG["print_log"]
    LOGGER_WRITE_TO_FILE: bool = LOGGER_CONFIG["write_to_file"]
    LOGGER_DISPLAY_MONITORING: bool = LOGGER_CONFIG["display_monitoring"]
    LOGGER_FILES_MONITORING: bool = LOGGER_CONFIG["files_monitoring"]
    LOGGER_FILE_SIZE_UNIT: str = LOGGER_CONFIG["file_size_unit"]
    LOGGER_DISK_ALERT_THRESHOLD_PERCENT: float = LOGGER_CONFIG[
        "disk_alert_threshold_percent"
    ]
    LOGGER_FILES_SIZE_ALERT_THRESHOLD_PERCENT: float = LOGGER_CONFIG[
        "log_files_size_alert_threshold_percent"
    ]
    LOGGER_MAX_LOG_FILE_SIZE: float = LOGGER_CONFIG["max_log_file_size"]
    LOGGER_IDENTIFIER_MAX_WIDTH: float = LOGGER_CONFIG["identifier_max_width"]
    LOGGER_FILENAME_LINENO_MAX_WIDTH: float = LOGGER_CONFIG["filename_lineno_max_width"]

    # Team config
    TEAM_CONFIG: dict = SPECIFIC_CONFIG["team_config"]
    DEFAULT_TEAM: str = TEAM_CONFIG["default_team"]
    INFO_BY_TEAM: dict[str, dict] = TEAM_CONFIG["info_by_team"]

    # Rolling Basis
    ROLLING_BASIS_CONFIG: dict = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER: int = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]

    ROLLING_BASIS_PIDS_CONFIG = ROLLING_BASIS_CONFIG["pids"]
    ROLLING_BASIS_PIDS_LINEAR_SPEED: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "linear_speed"
    ]
    ROLLING_BASIS_PIDS_ANGULAR_SPEED: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "angular_speed"
    ]
    ROLLING_BASIS_PIDS_LINEAR_POSITION: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "linear_position"
    ]
    ROLLING_BASIS_PIDS_ANGULAR_POSITION: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "angular_position"
    ]

    ROLLING_BASIS_SPEED_PROFILES_CONFIG: dict = ROLLING_BASIS_CONFIG["speed_profiles"]
    ROLLING_BASIS_DEFAULT_SPEED_PROFILE: dict[str:float] = (
        ROLLING_BASIS_SPEED_PROFILES_CONFIG["default"]
    )
    ROLLING_BASIS_HIGH_SPEED_PROFILE: dict[str:float] = (
        ROLLING_BASIS_SPEED_PROFILES_CONFIG["high"]
    )

    # Actuators
    ACTUATORS_CONFIG: dict = SPECIFIC_CONFIG["actuators"]
    ACTUATOR_TEENSY_SER: int = ACTUATORS_CONFIG["actuators_teensy_ser"]

    # Lidar
    LIDAR_CONFIG: dict = SPECIFIC_CONFIG["lidar"]
    LIDAR_ANGLES_UNIT: str = LIDAR_CONFIG["angles_unit"]
    LIDAR_DISTANCES_UNIT: str = LIDAR_CONFIG["distances_unit"]
    LIDAR_MIN_ANGLE: float = LIDAR_CONFIG["min_angle"]
    LIDAR_MAX_ANGLE: float = LIDAR_CONFIG["max_angle"]
    LIDAR_MIN_DISTANCE_DETECTION: float = LIDAR_CONFIG["min_distance_detection"]
    LIDAR_FRONTAL_DETECTION_ANGLE: float = LIDAR_CONFIG["frontal_detection_angle"]
    LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE: float = LIDAR_CONFIG[
        "semi_circular_detection_angle"
    ]

    # Arena
    ARENA_CONFIG: dict = CONFIG_STORE[ARENA_CONFIG_KEY]
    ARENA_BORDER_BUFFER: float = ARENA_CONFIG["border_buffer"]
    ARENA_OBSTACLE_BUFFER: float = ARENA_CONFIG["obstacle_buffer"]
    ARENA_CHUNK_SIZE: float = ARENA_CONFIG["chunk_size"]
    ARENA_FORBIDDEN_COVER_THRESHOLD: float = ARENA_CONFIG["forbidden_cover_threshold"]
