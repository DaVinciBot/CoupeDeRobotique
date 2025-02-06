# ====== Imports ======
# Standard library imports
import os
import datetime
from typing import Dict, Any, Type, TypeVar
from dataclasses import dataclass, field, fields, asdict

# Internal project imports
from logger.colors import BaseColors, ClassicColors
from logger.log_levels import LogLevels
from logger.tools import unpack_dict

# ====== Type Hints ======
T = TypeVar("T", bound="BaseConfig")


# ====== Configuration Classes ======
@dataclass
class BaseConfig:
    """
    Base configuration class with utility methods for creating instances from dictionaries.
    """

    @classmethod
    def from_dict(cls: Type[T], data: Dict[str, Any]) -> T:
        """
        Create an instance from a dictionary, ensuring correct instantiation of nested configurations.
        Automatically handles missing values by using default values.
        """
        default_instance = cls()
        updated_data = {
            f.name: data.get(f.name, getattr(default_instance, f.name))
            for f in fields(cls)
        }
        return cls(**updated_data)

    @classmethod
    def from_kwargs(cls: Type[T], **kwargs) -> T:
        """
        Create an instance from keyword arguments, supporting partial updates.
        """
        return cls.from_dict(kwargs)

    def get_attributes(self) -> Dict[str, Any]:
        """Return a dictionary of all attributes of the configuration instance."""
        return asdict(self)


@dataclass
class LogLevelsConfig(BaseConfig):
    """
    Configuration class for managing logging levels and output options.
    """
    decorator_log_level: LogLevels = LogLevels.DEBUG
    print_log_level: LogLevels = LogLevels.DEBUG
    file_log_level: LogLevels = LogLevels.DEBUG
    print_log: bool = True
    write_to_file: bool = True

    @classmethod
    def debug(cls):
        """Configuration for maximum debug logging."""
        return cls(LogLevels.DEBUG, LogLevels.DEBUG, LogLevels.DEBUG, True, True)

    @classmethod
    def info(cls):
        """Configuration for standard informational logging."""
        return cls(LogLevels.INFO, LogLevels.INFO, LogLevels.INFO, True, True)

    @classmethod
    def warning(cls):
        """Configuration for warning level logging."""
        return cls(LogLevels.WARNING, LogLevels.WARNING, LogLevels.WARNING, True, True)

    @classmethod
    def error(cls):
        """Configuration for error level logging only."""
        return cls(LogLevels.ERROR, LogLevels.ERROR, LogLevels.ERROR, True, True)

    @classmethod
    def critical(cls):
        """Configuration for critical level logging only."""
        return cls(LogLevels.CRITICAL, LogLevels.CRITICAL, LogLevels.CRITICAL, True, True)

    @classmethod
    def silent_debug(cls):
        """Configuration to disable logging."""
        return cls(LogLevels.WARNING, LogLevels.WARNING, LogLevels.DEBUG, True, True)

    @classmethod
    def silent(cls):
        """Configuration to disable print."""
        return cls(LogLevels.DEBUG, LogLevels.DEBUG, LogLevels.DEBUG, False, True)


@dataclass
class PlacementConfig(BaseConfig):
    """
    Configuration class for managing the placement of log components.
    """
    identifier_max_width: int = 0
    level_max_width: int = 0
    filename_lineno_max_width: int = 15
    placement_improvement: bool = True

    def adjust_placement(self, identifier: str):
        """Adjusts the placement of log components based on the provided identifier and log level."""
        if self.identifier_max_width == 0:
            self.identifier_max_width = len(identifier) + (2 if self.placement_improvement else 0)

        if self.level_max_width == 0:
            self.level_max_width = (
                    max(len(level.name) for level in LogLevels)
                    +
                    (2 if self.placement_improvement else 0)
            )


@dataclass
class MonitorConfig(BaseConfig):
    """
    Configuration class for monitoring log file size and disk space.
    """
    display_monitoring: bool = False
    files_monitoring: bool = True
    file_size_unit: str = "Go"
    file_size_precision: int = 2
    disk_alert_threshold_percent: float = 0.8
    log_files_size_alert_threshold_percent: float = 0.2
    max_log_file_size: float = 1.0

    def is_monitoring_enabled(self) -> bool:
        """Check if monitoring is enabled."""
        return self.display_monitoring or self.files_monitoring


@dataclass
class LoggerConfig:
    """
    Complete configuration class for logging system.
    """
    identifier: str = "unknown"
    log_levels_config: LogLevelsConfig = field(default_factory=LogLevelsConfig)
    placement_config: PlacementConfig = field(default_factory=PlacementConfig)
    monitor_config: MonitorConfig = field(default_factory=MonitorConfig)
    colors: type[BaseColors] = ClassicColors
    path: str = "logs"
    follow_logger_manager_rules: bool = False

    def _initialize_file_path(self):
        if not os.path.isdir(self.path):
            os.mkdir(self.path)
        self.full_path = os.path.join(self.path, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

    def __post_init__(self):
        if self.log_levels_config.write_to_file:
            self._initialize_file_path()

        self.placement_config.adjust_placement(self.identifier)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LoggerConfig":
        """
        Create an instance from a dictionary, ensuring nested configurations are properly instantiated.
        Partial updates are also supported.
        """
        return cls(
            identifier=data.get("identifier", cls.identifier),
            log_levels_config=LogLevelsConfig.from_dict(
                {**data, **data.get("log_levels_config", {})}
            ),
            placement_config=PlacementConfig.from_dict(
                {**data, **data.get("placement_config", {})}
            ),
            monitor_config=MonitorConfig.from_dict(
                {**data, **data.get("monitor_config", {})}
            ),
            colors=data.get("colors", cls.colors),
            path=data.get("path", cls.path),
            follow_logger_manager_rules=data.get("follow_logger_manager_rules", cls.follow_logger_manager_rules),
        )

    @classmethod
    def from_kwargs(cls, **kwargs) -> "LoggerConfig":
        """
        Create an instance from keyword arguments, supporting partial updates.
        """
        return cls.from_dict(kwargs)

    def get_attributes(self) -> dict[str, any]:
        """Return a dictionary of all attributes of the configuration instance."""
        return unpack_dict(asdict(self))
