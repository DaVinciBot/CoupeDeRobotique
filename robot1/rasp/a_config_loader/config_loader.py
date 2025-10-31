"""Utilities for testing the configuration loader."""

from __future__ import annotations

import json
import os
import pathlib
import sys
from typing import Any, ClassVar

from dotenv import load_dotenv
from loggerplusplus import LoggerConfig, LoggerManager, LogLevels, logger_colors

load_dotenv()


def load_json_file(file_path: pathlib.Path) -> dict[str, Any]:
    """Load a JSON file and return its content.

    Args:
        file_path (pathlib.Path): The path to the JSON file.

    Returns:
        dict[str, Any]: The content of the JSON file as a dictionary.
    """
    return json.load(file_path.open(encoding="utf-8"))


def get_env_bool(
    key: str,
    *,
    default: bool = False,
) -> bool:
    """Return a boolean loaded from the environment using ``keys`` priority order.

    Args:
        key (str):
            The environment variable name to check.
        default (bool):
            The default value to return if the environment variable is not set.

    Returns:
        bool: The boolean value of the environment variable.
    """
    raw_value = os.getenv(key, str(default))
    return raw_value == "True"


class CONFIG:
    """Configuration class to load and store configuration settings.

    Attributes:
        ROOT_DIR (pathlib.Path): The root directory of the project.
        COMMON_DIR (pathlib.Path): The path to the common directory.
        CONFIG_STORE (dict[str, Any]): The loaded configuration from config.json.

        GENERAL_CONFIG_KEY (str): Key for general configuration in the config file.
        SPECIFIC_CONFIG_KEY (str): Key for specific configuration in the config file.
        ARENA_CONFIG_KEY (str): Key for arena configuration in the config file.

        GENERAL_CONFIG (dict[str, Any]): General configuration settings.
        GENERAL_WS_CONFIG (dict[str, Any]): WebSocket configuration settings.
        GENERAL_TEENSY_CONFIG (dict[str, Any]): Teensy configuration settings.

        WS_PORT (int): WebSocket port.
        WS_CMD_ROUTE (str): WebSocket command route.
        WS_UI_ROUTE (str): WebSocket UI route.

        TEENSY_VID (int): Teensy USB vendor ID.
        TEENSY_PID (int): Teensy USB product ID.
        TEENSY_BAUDRATE (int): Baud rate for Teensy communication.
        TEENSY_CRC (bool): Whether to enable CRC for Teensy communication.

        SPECIFIC_CONFIG (dict[str, Any]): Specific configuration settings for the robot.
        SPECIFIC_WS_CONFIG (dict[str, Any]): Specific WebSocket configuration settings.
        SPECIFIC_WS_UI_CONFIG (dict[str, Any]):
            Specific WebSocket UI configuration settings.

        WS_SENDER_NAME (str): WebSocket sender name.
        WS_HOSTNAME (str): WebSocket hostname.
        WS_PING_PONG_INTERVAL (int): WebSocket ping-pong interval in seconds.

        WS_UI_SENDER_NAME (str): WebSocket UI sender name.
        WS_UI_HOSTNAME (str): WebSocket UI hostname.
        WS_UI_PING_PONG_INTERVAL (int): WebSocket UI ping-pong interval in seconds.

        ZOMBIE_MODE (bool): Whether the robot is in zombie mode.

        LOG_CONFIG (dict[str, Any]): Logging configuration settings.
        LOGGER_MANAGER_CONFIG (dict[str, Any]): Logger manager configuration settings.
        LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER (bool):
            Whether to enable file logs monitoring for one logger only.
        LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE (bool):
            Whether to enable dynamic config update for the logger
        LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER (bool):
            Whether to enable unique logger identifier.

        LOGGER_CONFIG (dict[str, Any]): Logger configuration settings.
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
        LOGGER_FILES_SIZE_ALERT_THRESHOLD_PERCENT (float):
            Log files size alert threshold percentage.
        LOGGER_MAX_LOG_FILE_SIZE (float): Maximum size for log files.
        LOGGER_IDENTIFIER_MAX_WIDTH (float): Maximum width for logger identifier.
        LOGGER_FILENAME_LINENO_MAX_WIDTH (float):
            Maximum width for filename and line number in logs.

        TEAM_CONFIG (dict[str, Any]): Team configuration settings.
        DEFAULT_TEAM (str): Default team color.
        INFO_BY_TEAM (dict[str, Any]): Information by team.

        SCORE_CONFIG (dict[str, Any]): Scoring system configuration settings.

        BUILD_ONE_FLOOR (int): Score for building one floor.
        BUILD_TWO_FLOORS (int): Score for building two floors.
        GO_TO_BACKSTAGE (int): Score for going to backstage.
        BANNER (int): Score for displaying banner.

        OCCUPIED_ZONE (int): Score for occupying a zone.
        SUPERSTAR_ON_STAGE (int): Score for having a superstar on stage.
        PARTYING (int): Score for partying.
        FREE_STAGE_ZONE (int): Score for being in a free stage zone.

        ROLLING_BASIS_CONFIG (dict[str, Any]): Rolling basis configuration settings.
        ROLLING_BASIS_TEENSY_SER (int): Serial number for the rolling basis Teensy.

        ROLLING_BASIS_PIDS_CONFIG (dict[str, Any]):
            PID configuration for the rolling basis.
        ROLLING_BASIS_PIDS_LINEAR_POSITION (dict[str, float]):
            PID settings for linear position
        ROLLING_BASIS_PIDS_ANGULAR_POSITION (dict[str, float]):
            PID settings for angular position.

        ROLLING_BASIS_SPEED_PROFILES_CONFIG (dict[str, Any]):
            Speed profiles configuration for the rolling basis.
        ROLLING_BASIS_SPEED_PROFILES_LINEAR (dict[str, Any]): Linear speed profiles.
        ROLLING_BASIS_SPEED_PROFILES_ANGULAR (dict[str, Any]): Angular speed profiles.

        ROLLING_BASIS_DEFAULT_SPEED_PROFILER (SpeedProfiler): Default speed profiler
        ROLLING_BASIS_SLOW_SPEED_PROFILER (SpeedProfiler): Slow speed profiler
        ROLLING_BASIS_SPEED_PROFILER_PID (SpeedProfiler): Speed profiler for PID control

        ACTUATORS_CONFIG (dict[str, Any]): Actuators configuration settings.
        ACTUATOR_TEENSY_SER (int): Serial number for the actuators Teensy
        ACTUATOR_SERVOS_CONFIG (ClassVar[dict[int, Any]]):
            Servos configuration for the actuators
        ACTUATOR_ELEVATOR_CONFIG (dict[str, Any]):
            Elevator configuration for the actuators
        ACTUATOR_DELAY (float): Delay for the actuators

        LIDAR_CONFIG (dict[str, Any]): Lidar configuration settings.
        LIDAR_ANGLES_UNIT (str): Unit for lidar angles.
        LIDAR_DISTANCES_UNIT (str): Unit for lidar distances.
        LIDAR_MIN_ANGLE (float): Minimum angle for lidar detection.
        LIDAR_MAX_ANGLE (float): Maximum angle for lidar detection.
        LIDAR_MIN_DISTANCE_DETECTION (float): Minimum distance for lidar detection.
        LIDAR_FRONTAL_DETECTION_ANGLE (float): Frontal detection angle for lidar
        LIDAR_SEMI_CIRCULAR_DETECTION_ANGLE (float):
            Semi-circular detection angle for lidar.

        ARENA_CONFIG (dict[str, Any]): Arena configuration settings.
        ARENA_BORDER_BUFFER (float): Buffer size for arena borders.
        ARENA_OBSTACLE_BUFFER (float): Buffer size for arena obstacles.
        ARENA_CHUNK_SIZE (int): Size of the arena chunks.
        ARENA_FORBIDDEN_COVER_THRESHOLD (float):
            Threshold for forbidden cover in the arena.

        MOVEMENT_MANAGER_CONFIG (dict[str, Any]):
            Movement manager configuration settings.
        MOVEMENT_MANAGER_MOVEMENT_RESOLUTION (float):
            Movement resolution for the movement manager.

        ACS_PROFILES_CONFIG (dict[str, Any]):
            ACS profiles configuration for the movement manager.
        ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_FINISH_GAME (BaseAcsDetectionProfileParams):
            ACS profile for going to color reserved zone to finish game.
        ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_CONSTRUCT (BaseAcsDetectionProfileParams):
            ACS profile for going to color reserved zone to construct.
        ACS_PROFILE_GO_TO_STUFF_ZONE_TO_PICK_UP (BaseAcsDetectionProfileParams):
            ACS profile for going to stuff zone to pick up.
        ACS_PROFILE_BACKWARD (BaseAcsDetectionProfileParams):
            ACS profile for backward movement.
        ACS_PROFILE_PRECISE_FORWARD (BaseAcsDetectionProfileParams):
            ACS profile for precise forward movement.
        ACS_PROFILE_START_TASK (BaseAcsDetectionProfileParams):
            ACS profile for starting a task.

        JACK_PIN (int): Pin number for the jack.
        BAU_PIN (int): Pin number for the BAU.

        LIDAR_DUMMY (bool): Whether to enable dummy mode for the lidar sensor.
        ROLLING_BASIS_DUMMY (bool): Whether to enable dummy mode for the rolling basis.
        ACTUATORS_DUMMY (bool): Whether to enable dummy mode for the actuators.
    """

    # Directory path (dont't touch)
    ROOT_DIR: pathlib.Path = (
        pathlib.Path(__file__).resolve().parent.parent.parent.parent
    )

    COMMON_DIR: pathlib.Path = ROOT_DIR / "common"
    sys.path.append(
        str(COMMON_DIR),
    )  # Add common directory to the path (to be able to import common modules)
    CONFIG_STORE: dict[str, Any] = load_json_file(ROOT_DIR / "config.json")
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501, PLC0415
        BaseAcsDetectionProfileParams,
    )
    from navigation.trajectory_planner.speed_profile import (  # noqa: PLC0415
        BasicSpeedProfile,
        LinearRampedSpeedProfile,
        SpeedProfiler,
    )

    # TO CONFIG !
    GENERAL_CONFIG_KEY: str = "general"
    SPECIFIC_CONFIG_KEY: str = "rob"
    ARENA_CONFIG_KEY: str = "arena"

    # CONSTANTS TO DEFINE !
    # General config
    GENERAL_CONFIG: dict[str, Any] = CONFIG_STORE[GENERAL_CONFIG_KEY]
    GENERAL_WS_CONFIG: dict[str, Any] = GENERAL_CONFIG["ws"]
    GENERAL_TEENSY_CONFIG: dict[str, Any] = GENERAL_CONFIG["teensy"]

    WS_PORT: int = int(GENERAL_WS_CONFIG["port"])
    WS_CMD_ROUTE: str = GENERAL_WS_CONFIG["cmd_route"]
    WS_UI_ROUTE: str = GENERAL_WS_CONFIG["ui_route"]

    TEENSY_VID: int = GENERAL_TEENSY_CONFIG["vid"]
    TEENSY_PID: int = GENERAL_TEENSY_CONFIG["pid"]
    TEENSY_BAUDRATE: int = GENERAL_TEENSY_CONFIG["baudrate"]
    TEENSY_CRC: bool = GENERAL_TEENSY_CONFIG["crc"]

    # Specific config
    SPECIFIC_CONFIG: dict[str, Any] = CONFIG_STORE[SPECIFIC_CONFIG_KEY]

    # Specific ws config
    SPECIFIC_WS_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["ws"]
    SPECIFIC_WS_UI_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["ws_ui"]

    WS_SENDER_NAME: str = SPECIFIC_WS_CONFIG["sender_name"]
    WS_HOSTNAME: str = SPECIFIC_WS_CONFIG["hostname"]
    WS_PING_PONG_INTERVAL: int = int(SPECIFIC_WS_CONFIG["ping_pong_interval"])

    WS_UI_SENDER_NAME: str = SPECIFIC_WS_UI_CONFIG["sender_name"]
    WS_UI_HOSTNAME: str = SPECIFIC_WS_UI_CONFIG["hostname"]
    WS_UI_PING_PONG_INTERVAL: int = int(SPECIFIC_WS_UI_CONFIG["ping_pong_interval"])

    # Zombie mode
    ZOMBIE_MODE: bool = (
        True
        if any(flag in sys.argv for flag in ("-z", "--zombie"))
        else (
            False
            if any(flag in sys.argv for flag in ("-g", "--game"))
            else SPECIFIC_CONFIG["zombie_mode"]
        )
    )

    # Logs
    LOG_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["log"]

    LOGGER_MANAGER_CONFIG: dict[str, Any] = LOG_CONFIG["logger_manager"]
    LOGGER_MANAGER_ENABLE_FILES_LOGS_MONITORING_ONLY_FOR_ONE_LOGGER: bool = (
        LOGGER_MANAGER_CONFIG["enable_files_logs_monitoring_only_for_one_logger"]
    )
    LOGGER_MANAGER_ENABLE_DYNAMIC_CONFIG_UPDATE: bool = LOGGER_MANAGER_CONFIG[
        "enable_dynamic_config_update"
    ]
    LOGGER_MANAGER_ENABLE_UNIQUE_LOGGER_IDENTIFIER: bool = LOGGER_MANAGER_CONFIG[
        "enable_unique_logger_identifier"
    ]

    LOGGER_CONFIG: dict[str, Any] = LOG_CONFIG["logger"]
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
    TEAM_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["team_config"]
    DEFAULT_TEAM: str = TEAM_CONFIG["default_team"]
    INFO_BY_TEAM: dict[str, Any] = TEAM_CONFIG["info_by_team"]

    # Scoring System
    SCORE_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["score"]

    # Boombot
    BUILD_ONE_FLOOR: int = SCORE_CONFIG["boombot"]["build_one_floor"]
    BUILD_TWO_FLOORS: int = SCORE_CONFIG["boombot"]["build_two_floors"]
    GO_TO_BACKSTAGE: int = SCORE_CONFIG["boombot"]["go_to_backstage"]
    BANNER: int = SCORE_CONFIG["boombot"]["banner"]

    # PAMIs
    OCCUPIED_ZONE: int = SCORE_CONFIG["pamis"]["occupied_zone"]
    SUPERSTAR_ON_STAGE: int = SCORE_CONFIG["pamis"]["superstar_on_stage"]
    PARTYING: int = SCORE_CONFIG["pamis"]["partying"]
    FREE_STAGE_ZONE: int = SCORE_CONFIG["pamis"]["free_stage_zone"]

    # Rolling Basis
    ROLLING_BASIS_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["rolling_basis"]
    ROLLING_BASIS_TEENSY_SER: int = ROLLING_BASIS_CONFIG["rolling_basis_teensy_ser"]

    ROLLING_BASIS_PIDS_CONFIG: dict[str, Any] = ROLLING_BASIS_CONFIG["pids"]
    ROLLING_BASIS_PIDS_LINEAR_POSITION: dict[str, float] = ROLLING_BASIS_PIDS_CONFIG[
        "linear_position"
    ]
    ROLLING_BASIS_PIDS_ANGULAR_POSITION: dict[str, float] = ROLLING_BASIS_PIDS_CONFIG[
        "angular_position"
    ]

    ROLLING_BASIS_SPEED_PROFILES_CONFIG: dict[str, Any] = ROLLING_BASIS_CONFIG[
        "speed_profiles"
    ]
    ROLLING_BASIS_SPEED_PROFILES_LINEAR: dict[str, Any] = (
        ROLLING_BASIS_SPEED_PROFILES_CONFIG["linear_speed"]
    )
    ROLLING_BASIS_SPEED_PROFILES_ANGULAR: dict[str, Any] = (
        ROLLING_BASIS_SPEED_PROFILES_CONFIG["angular_speed"]
    )

    ROLLING_BASIS_DEFAULT_SPEED_PROFILER: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=LinearRampedSpeedProfile(
            **ROLLING_BASIS_SPEED_PROFILES_LINEAR["default"],
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"],
        ),
    )
    ROLLING_BASIS_SLOW_SPEED_PROFILER: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=LinearRampedSpeedProfile(
            **ROLLING_BASIS_SPEED_PROFILES_LINEAR["slow"],
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"],
        ),
    )
    ROLLING_BASIS_SPEED_PROFILER_PID: SpeedProfiler = SpeedProfiler(
        linear_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_LINEAR["default"]["max_speed"],
        ),
        angular_speed_profile=BasicSpeedProfile(
            ROLLING_BASIS_SPEED_PROFILES_ANGULAR["default"]["speed"],
        ),
    )

    # Actuators
    ACTUATORS_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["actuators"]
    ACTUATOR_TEENSY_SER: int = ACTUATORS_CONFIG["actuators_teensy_ser"]
    ACTUATOR_SERVOS_CONFIG: ClassVar[dict[int, Any]] = {
        int(k): v for k, v in ACTUATORS_CONFIG["servos_config"].items()
    }
    ACTUATOR_ELEVATOR_CONFIG: dict[str, Any] = ACTUATORS_CONFIG["elevator"]
    ACTUATOR_DELAY: float = ACTUATORS_CONFIG["delay"]

    # Lidar
    LIDAR_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["lidar"]
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
    ARENA_CONFIG: dict[str, Any] = CONFIG_STORE[ARENA_CONFIG_KEY]
    ARENA_BORDER_BUFFER: float = ARENA_CONFIG["border_buffer"]
    ARENA_OBSTACLE_BUFFER: float = ARENA_CONFIG["obstacle_buffer"]
    ARENA_CHUNK_SIZE: int = int(ARENA_CONFIG["chunk_size"])
    ARENA_FORBIDDEN_COVER_THRESHOLD: float = ARENA_CONFIG["forbidden_cover_threshold"]
    ARENA_WIDTH: float = ARENA_CONFIG["width"]
    ARENA_HEIGHT: float = ARENA_CONFIG["height"]

    # Movement manager
    MOVEMENT_MANAGER_CONFIG: dict[str, Any] = SPECIFIC_CONFIG["movement_manager"]
    MOVEMENT_MANAGER_MOVEMENT_RESOLUTION: float = MOVEMENT_MANAGER_CONFIG[
        "movement_resolution"
    ]

    # ACS Detection Profiles
    ACS_PROFILES_CONFIG: dict[str, Any] = MOVEMENT_MANAGER_CONFIG["acs_profiles"]
    ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_FINISH_GAME: BaseAcsDetectionProfileParams = BaseAcsDetectionProfileParams.from_config(
        **ACS_PROFILES_CONFIG["go_to_color_reserved_zone_to_finish_game"],
    )
    ACS_PROFILE_GO_TO_COLOR_RESERVED_ZONE_TO_CONSTRUCT: BaseAcsDetectionProfileParams = BaseAcsDetectionProfileParams.from_config(
        **ACS_PROFILES_CONFIG["go_to_color_reserved_zone_to_construct"],
    )
    ACS_PROFILE_GO_TO_STUFF_ZONE_TO_PICK_UP: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(
            **ACS_PROFILES_CONFIG["go_to_stuff_zone_to_pick_up"],
        )
    )
    ACS_PROFILE_BACKWARD: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(**ACS_PROFILES_CONFIG["backward"])
    )
    ACS_PROFILE_PRECISE_FORWARD: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(
            **ACS_PROFILES_CONFIG["precise_forward"],
        )
    )
    ACS_PROFILE_START_TASK: BaseAcsDetectionProfileParams = (
        BaseAcsDetectionProfileParams.from_config(**ACS_PROFILES_CONFIG["start_task"])
    )

    # Jack
    JACK_PIN: int = SPECIFIC_CONFIG["jack"]["pin"]

    # BAU
    BAU_PIN: int = SPECIFIC_CONFIG["bau"]["pin"]

    # Dummy modes
    LIDAR_DUMMY: bool = get_env_bool("LIDAR_DUMMY")
    ROLLING_BASIS_DUMMY: bool = get_env_bool("ROLLING_BASIS_DUMMY")
    ACTUATORS_DUMMY: bool = get_env_bool("ACTUATORS_DUMMY")


# Logger: LoggerManager + global configuration

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
