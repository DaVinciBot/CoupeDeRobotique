import pathlib
import json
import sys
import os


def load_json_file(file_path):
    try:
        with open(file_path) as config:
            file_json = json.load(config)
    except Exception:
        raise

    return file_json


class CONFIG:
    # TO CONFIG !
    SPECIFIC_CONFIG_KEY = "rob"
    GENERAL_CONFIG_KEY = "general"
    ARENA_CONFIG_KEY = "arena"

    # Directory path (dont't touch)
    ROOT_DIR = pathlib.Path(__file__).resolve().parent.parent.parent

    COMMON_DIR = os.path.join(ROOT_DIR, "common")
    sys.path.append(
        COMMON_DIR
    )  # Add common directory to the path (to be able to import common modules)
    CONFIG_STORE = load_json_file(os.path.join(ROOT_DIR, "config.json"))

    from navigation import (
        SpeedProfiler,
        BasicSpeedProfile,
        LinearRampedSpeedProfile,
        BaseAcsDetectionProfileParams,
    )

    # CONSTANTS TO DEFINE !
    # General config
    GENERAL_CONFIG = CONFIG_STORE[GENERAL_CONFIG_KEY]
    GENERAL_WS_CONFIG = GENERAL_CONFIG["ws"]
    GENERAL_TEENSY_CONFIG = GENERAL_CONFIG["teensy"]

    WS_PORT = int(GENERAL_WS_CONFIG["port"])
    WS_CMD_ROUTE = GENERAL_WS_CONFIG["cmd_route"]
    WS_UI_ROUTE = GENERAL_WS_CONFIG["ui_route"]

    TEENSY_VID = GENERAL_TEENSY_CONFIG["vid"]
    TEENSY_PID = GENERAL_TEENSY_CONFIG["pid"]
    TEENSY_BAUDRATE = GENERAL_TEENSY_CONFIG["baudrate"]
    TEENSY_CRC = GENERAL_TEENSY_CONFIG["crc"]
    TEENSY_DUMMY = GENERAL_TEENSY_CONFIG["dummy"]

    # Specific config
    SPECIFIC_CONFIG = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG = SPECIFIC_CONFIG["ws"]
    SPECIFIC_WS_UI_CONFIG = SPECIFIC_CONFIG["ws_ui"]

    WS_SENDER_NAME = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])

    WS_UI_SENDER_NAME = SPECIFIC_WS_UI_CONFIG["sender_name"]
    WS_UI_HOSTNAME = SPECIFIC_WS_UI_CONFIG["hostname"]
    WS_UI_PING_PONG_INTERVAL = int(SPECIFIC_WS_UI_CONFIG["ping_pong_interval"])

    # Zombie mode
    ZOMBIE_MODE = SPECIFIC_CONFIG["zombie_mode"]
    if "-z" in sys.argv or "--zombie" in sys.argv:
        ZOMBIE_MODE = True
    if "-g" in sys.argv or "--game" in sys.argv:
        ZOMBIE_MODE = False

    # Logs
    LOG_CONFIG = SPECIFIC_CONFIG["log"]

    LOGGER_MANAGER_CONFIG = LOG_CONFIG["logger_manager"]
    LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER = (
        LOGGER_MANAGER_CONFIG["enable_files_logs_monitoring_only_for_one_logger"]
    )
    LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE = LOGGER_MANAGER_CONFIG[
        "enable_dynamic_config_update"
    ]
    LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER = LOGGER_MANAGER_CONFIG[
        "enable_unique_logger_identifier"
    ]

    LOGGER_CONFIG = LOG_CONFIG["logger"]
    LOGGER_COLORS = LOGGER_CONFIG["colors"]
    LOGGER_PATH = LOGGER_CONFIG["path"]
    LOGGER_DECORATOR_LOG_LEVEL = LOGGER_CONFIG["decorator_log_level"]
    LOGGER_PRINT_LOG_LEVEL = LOGGER_CONFIG["print_log_level"]
    LOGGER_FILE_LOG_LEVEL = LOGGER_CONFIG["file_log_level"]
    LOGGER_PRINT_LOG = LOGGER_CONFIG["print_log"]
    LOGGER_WRITE_TO_FILE = LOGGER_CONFIG["write_to_file"]
    LOGGER_DISPLAY_MONITORING = LOGGER_CONFIG["display_monitoring"]
    LOGGER_FILES_MONITORING = LOGGER_CONFIG["files_monitoring"]
    LOGGER_FILE_SIZE_UNIT = LOGGER_CONFIG["file_size_unit"]
    LOGGER_DISK_ALERT_THRESHOLD_PERCENT = LOGGER_CONFIG["disk_alert_threshold_percent"]
    LOGGER_FILES_SIZE_ALERT_THRESHOLD_PERCENT = LOGGER_CONFIG[
        "log_files_size_alert_threshold_percent"
    ]
    LOGGER_MAX_LOG_FILE_SIZE = LOGGER_CONFIG["max_log_file_size"]
    LOGGER_IDENTIFIER_MAX_WIDTH = LOGGER_CONFIG["identifier_max_width"]
    LOGGER_FILENAME_LINENO_MAX_WIDTH = LOGGER_CONFIG["filename_lineno_max_width"]

    # Team config
    TEAM_CONFIG = SPECIFIC_CONFIG["team_config"]
    DEFAULT_TEAM: str = TEAM_CONFIG["default_team"]
    INFO_BY_TEAM: dict[str, dict] = TEAM_CONFIG["info_by_team"]

    # Scoring System
    SCORE_CONFIG = SPECIFIC_CONFIG["score"]

    # Boombot
    BUILD_ONE_FLOOR = SCORE_CONFIG["boombot"]["build_one_floor"]
    BUILD_TWO_FLOORS = SCORE_CONFIG["boombot"]["build_two_floors"]
    GO_TO_BACKSTAGE = SCORE_CONFIG["boombot"]["go_to_backstage"]
    BANNER = SCORE_CONFIG["boombot"]["banner"]

    # PAMIs
    OCCUPIED_ZONE = SCORE_CONFIG["pamis"]["occupied_zone"]
    SUPERSTAR_ON_STAGE = SCORE_CONFIG["pamis"]["superstar_on_stage"]
    PARTYING = SCORE_CONFIG["pamis"]["partying"]
    FREE_STAGE_ZONE = SCORE_CONFIG["pamis"]["free_stage_zone"]

    # Rolling Basis
    ROLLING_BASIS_CONFIG = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]

    ROLLING_BASIS_PIDS_CONFIG = ROLLING_BASIS_CONFIG["pids"]
    ROLLING_BASIS_PIDS_LINEAR_POSITION: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "linear_position"
    ]
    ROLLING_BASIS_PIDS_ANGULAR_POSITION: dict[str:float] = ROLLING_BASIS_PIDS_CONFIG[
        "angular_position"
    ]

    ROLLING_BASIS_SPEED_PROFILES_CONFIG = ROLLING_BASIS_CONFIG["speed_profiles"]
    ROLLING_BASIS_SPEED_PROFILES_LINEAR = ROLLING_BASIS_SPEED_PROFILES_CONFIG[
        "linear_speed"
    ]
    ROLLING_BASIS_SPEED_PROFILES_ANGULAR = ROLLING_BASIS_SPEED_PROFILES_CONFIG[
        "angular_speed"
    ]

    ROLLING_BASIS_DEFAULT_SPEED_PROFILER: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=LinearRampedSpeedProfile(
            **ROLLING_BASIS_SPEED_PROFILES_LINEAR["default"]
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"]
        ),
    )
    ROLLING_BASIS_SLOW_SPEED_PROFILER: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=LinearRampedSpeedProfile(
            **ROLLING_BASIS_SPEED_PROFILES_LINEAR["slow"]
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"]
        ),
    )
    ROLLING_BASIS_SPEED_PROFILER_PID: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_LINEAR["default"]["max_speed"]
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"]
        ),
    )

    # Actuators
    ACTUATORS_CONFIG = SPECIFIC_CONFIG["actuators"]
    ACTUATOR_TEENSY_SER = ACTUATORS_CONFIG["actuators_teensy_ser"]
    ACTUATOR_SERVOS_CONFIG = ACTUATORS_CONFIG["servos_config"]
    ACTUATOR_SERVOS_CONFIG = {int(k): v for k, v in ACTUATOR_SERVOS_CONFIG.items()}

    ACTUATOR_ELEVATOR_CONFIG = ACTUATORS_CONFIG["elevator"]
    ACTUATOR_DELAY = ACTUATORS_CONFIG["delay"]

    # Lidar
    LIDAR_CONFIG = SPECIFIC_CONFIG["lidar"]
    LIDAR_ANGLES_UNIT = LIDAR_CONFIG["angles_unit"]
    LIDAR_DISTANCES_UNIT = LIDAR_CONFIG["distances_unit"]
    LIDAR_MIN_ANGLE = LIDAR_CONFIG["min_angle"]
    LIDAR_MAX_ANGLE = LIDAR_CONFIG["max_angle"]
    LIDAR_MIN_DISTANCE_DETECTION = LIDAR_CONFIG["min_distance_detection"]
    LIDAR_FRONTAL_DETECTION_ANGLE = LIDAR_CONFIG["frontal_detection_angle"]
    LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE = LIDAR_CONFIG["semi_circular_detection_angle"]

    # Arena
    ARENA_CONFIG = CONFIG_STORE[ARENA_CONFIG_KEY]
    ARENA_BORDER_BUFFER = ARENA_CONFIG["border_buffer"]
    ARENA_OBSTACLE_BUFFER = ARENA_CONFIG["obstacle_buffer"]
    ARENA_CHUNK_SIZE = ARENA_CONFIG["chunk_size"]
    ARENA_FORBIDDEN_COVER_THRESHOLD = ARENA_CONFIG["forbidden_cover_threshold"]

    # Movement manager
    MOVEMENT_MANAGER_CONFIG = SPECIFIC_CONFIG["movement_manager"]
    MOVEMENT_MANAGER_MOVEMENT_RESOLUTION = MOVEMENT_MANAGER_CONFIG[
        "movement_resolution"
    ]

    # ACS Detection Profiles
    ACS_PROFILES_CONFIG = MOVEMENT_MANAGER_CONFIG["acs_profiles"]
    ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_FINISH_GAME: (
        BaseAcsDetectionProfileParams
    ) = BaseAcsDetectionProfileParams.from_config(
        **ACS_PROFILES_CONFIG["go_to_color_reserved_zone_to_finish_game"]
    )
    ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_CONSTRUCT: (
        BaseAcsDetectionProfileParams
    ) = BaseAcsDetectionProfileParams.from_config(
        **ACS_PROFILES_CONFIG["go_to_color_reserved_zone_to_construct"]
    )
    ACS_PROFILE_GO_TO_STUFF_ZONE_TO_PICK_UP: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(
            **ACS_PROFILES_CONFIG["go_to_stuff_zone_to_pick_up"]
        )
    )
    ACS_PROFILE_BACKWARD: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(**ACS_PROFILES_CONFIG["backward"])
    )
    ACS_PROFILE_PRECISE_FORWARD: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(
            **ACS_PROFILES_CONFIG["precise_forward"]
        )
    )
    ACS_PROFILE_START_TASK: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(**ACS_PROFILES_CONFIG["start_task"])
    )

    # Jack
    JACK_PIN = SPECIFIC_CONFIG["jack"]["pin"]

    # BAU
    BAU_PIN = SPECIFIC_CONFIG["bau"]["pin"]


# Logger: LoggerManager + global configuration
from loggerplusplus import LoggerManager, LogLevels, LoggerConfig, logger_colors

LoggerManager.enable_files_logs_monitoring_only_for_one_logger = (
    CONFIG.LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER
)
LoggerManager.enable_dynamic_config_update = (
    CONFIG.LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE
)
LoggerManager.enable_unique_logger_identifier = (
    CONFIG.LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER
)

LoggerManager.global_config = LoggerConfig.from_kwargs(
    colors=getattr(logger_colors, CONFIG.LOGGER_COLORS),
    path=CONFIG.LOGGER_PATH,
    # LogLevels
    decorator_log_level=getattr(LogLevels, CONFIG.LOGGER_DECORATOR_LOG_LEVEL),
    print_log_level=getattr(LogLevels, CONFIG.LOGGER_PRINT_LOG_LEVEL),
    file_log_level=getattr(LogLevels, CONFIG.LOGGER_FILE_LOG_LEVEL),
    # Loggers Output
    print_log=CONFIG.LOGGER_PRINT_LOG,
    write_to_file=CONFIG.LOGGER_WRITE_TO_FILE,
    # Monitoring
    display_monitoring=CONFIG.LOGGER_DISPLAY_MONITORING,
    files_monitoring=CONFIG.LOGGER_FILES_MONITORING,
    file_size_unit=CONFIG.LOGGER_FILE_SIZE_UNIT,
    disk_alert_threshold_percent=CONFIG.LOGGER_DISK_ALERT_THRESHOLD_PERCENT,
    log_files_size_alert_threshold_percent=CONFIG.LOGGER_FILES_SIZE_ALERT_THRESHOLD_PERCENT,
    max_log_file_size=CONFIG.LOGGER_MAX_LOG_FILE_SIZE,
    # Placement
    identifier_max_width=CONFIG.LOGGER_IDENTIFIER_MAX_WIDTH,
    filename_lineno_max_width=CONFIG.LOGGER_FILENAME_LINENO_MAX_WIDTH,
)
