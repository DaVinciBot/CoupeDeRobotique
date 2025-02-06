# ====== Code Summary ======
# This module enhances Python's built-in logging by adding a distinct 'FATAL' log level,
# improving log formatting, and enabling color-coded log messages for better readability.
# It provides a custom Logger class that supports console and file logging with adjustable
# color settings, ensuring clear and structured log outputs.
#
# Additionally, the logger includes a monitoring system that automatically deletes
# excessive logs to prevent overflow, displays the remaining disk space, and offers
# various practical features for efficient log management.


# ====== Imports ======
# Standard library imports
from typing import Optional
import logging
import sys

# Third-party library imports
from colorama import just_fix_windows_console

# Internal project imports
from logger.log_levels import LogLevels
from logger.monitoring import DiskMonitor
from logger.formatter import Formatter
from logger.colors import BaseColors
from logger.logger_configs import LoggerConfig
from logger.logger_manager import LoggerManager

# ====== Initialize Console for Colors ======
just_fix_windows_console()  # Enables colors in windows consoles (why not)

# ====== Modification of Native Logging Behavior ======
# Python's logging module treats 'CRITICAL' and 'FATAL' as synonyms.
# To distinguish 'FATAL' as a unique severity level, we manually add it.
logging.addLevelName(LogLevels.FATAL, "FATAL")


# Define a method for the Logger class to log messages at 'FATAL' level.
def class_fatal(self: logging.Logger, msg: str, *args, **kwargs):
    """
    Log 'msg % args' with severity 'FATAL'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    This allows using `logger.fatal()` as a distinct logging level.

    logger.fatal("Houston, we have one %s", "major disaster", exc_info=True)

    Args:
        self (Logger): The logger instance.
        msg (str): The message to log.
    """
    if self.isEnabledFor(LogLevels.FATAL):
        self._log(LogLevels.FATAL, msg, args, **kwargs)


# Attach the new 'fatal' method to the logging.Logger class.
logging.Logger.fatal = class_fatal


# Define a global function to log fatal messages using the root logger.
def fatal(msg, *args, **kwargs):
    """
    Log a message with severity 'CRITICAL' on the root logger. If the logger
    has no handlers, call basicConfig() to add a console handler with a
    pre-defined format.
    """
    if len(logging.root.handlers) == 0:
        logging.basicConfig()
    logging.root.critical(msg, *args, **kwargs)


# ====== Logger Class ======
class Logger:
    """
        Custom Logger class that extends Python's built-in logging functionality.
        Supports console and file logging with customizable settings, including colored
        output for improved readability in terminals.
        """

    # ====== Initialization Methods ======

    @staticmethod
    def _initialize_config(kwargs) -> LoggerConfig:
        """
        Initializes logger configuration from provided keyword arguments.
        If a LoggerConfig instance is provided, it is used directly; otherwise,
        configuration is generated from given keyword arguments.

        Args:
            kwargs (dict): Keyword arguments for configuring the logger.

        Returns:
            LoggerConfig: Configured logger instance.
        """
        config = kwargs.get("config")
        if isinstance(config, LoggerConfig):
            return config
        return LoggerConfig.from_kwargs(**kwargs)

    def __init__(self, **kwargs):
        """
        Initialize the logger with customizable parameters.

        Supports:
        - Full dictionary configuration
        - Partial updates of specific configurations
        - Directly passing configuration objects (LogLevelsConfig, PlacementConfig, etc.)
        """

        self.config = self._initialize_config(kwargs)

        # Register the logger with the LoggerManager for centralized tracking
        LoggerManager.register_logger(self)

        # Perform post-initialization setup
        self.__post_init__()

    def _get_log_level_to_logger_function_map(self) -> dict[LogLevels, callable]:
        """
        Creates a mapping of log levels to the corresponding logging methods.

        Returns:
            dict: A dictionary mapping LogLevels to logging methods.
        """
        return {
            LogLevels.FATAL: self.logger.fatal,
            LogLevels.CRITICAL: self.logger.critical,
            LogLevels.ERROR: self.logger.error,
            LogLevels.WARNING: self.logger.warning,
            LogLevels.INFO: self.logger.info,
            LogLevels.DEBUG: self.logger.debug,
        }

    def __post_init__(self):
        """
        Post-initialization setup for the logger instance.
        - Checks if logger already exists to avoid duplicate handlers.
        - Configures disk monitoring if enabled.
        - Sets up logging handlers if necessary.
        """
        already_exists = self.config.identifier in logging.root.manager.loggerDict

        self.logger = logging.getLogger(self.config.identifier)
        self.logger.setLevel(LogLevels.DEBUG)  # Set the lowest level to capture all messages

        if self.config.monitor_config.is_monitoring_enabled():
            self.disk_monitor = DiskMonitor(
                logger=self,
                directory=self.config.path,
                config=self.config.monitor_config
            )

        if not already_exists:
            self._setup_handlers()

        self.log_level_to_logger_function = self._get_log_level_to_logger_function_map()

        if self.config.monitor_config.display_monitoring and not already_exists:
            self.disk_monitor.display_monitoring()
        if self.config.monitor_config.files_monitoring and not already_exists:
            self.disk_monitor.clean_logs()

    # ====== Handlers Methods ======
    def _setup_handlers(self):
        """Sets up logging handlers for console and file output."""
        if self.config.log_levels_config.print_log:
            self._set_handler(
                logging.StreamHandler(stream=sys.stdout),
                self.config.log_levels_config.print_log_level,
                self.config.colors
            )
        if self.config.log_levels_config.write_to_file:
            self._set_handler(
                logging.FileHandler(self.config.full_path),
                self.config.log_levels_config.file_log_level,
                colors=None
            )

    def _set_handler(self, handler: logging.Handler, level: int, colors: Optional[type[BaseColors]]):
        """
        Configures a given handler with a formatter and logging level.

        Args:
            handler (logging.Handler): The logging handler to configure.
            level (int): The logging level for this handler.
            colors (Optional[type[BaseColors]]): Color settings for console output.
        """
        formatter = Formatter(
            identifier=self.config.identifier,
            identifier_max_width=self.config.placement_config.identifier_max_width,
            filename_lineno_max_width=self.config.placement_config.filename_lineno_max_width,
            level_max_width=self.config.placement_config.level_max_width,
            colors=colors,
        )
        handler.setLevel(level)
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    # ====== Formatter Methods ======
    def update_handler_formatter(
            self,
            handler_type: type[logging.FileHandler] | type[logging.StreamHandler],
            identifier: Optional[str] = None,
            identifier_max_width: Optional[int] = None,
            filename_lineno_max_width: Optional[int] = None,
            level_max_width: Optional[int] = None,
            colors: Optional[type[BaseColors]] = None,
            **kwargs
    ):
        """
        Updates the formatter of a specified handler type dynamically.

        Args:
            handler_type (type[logging.FileHandler] | type[logging.StreamHandler]):
                The logging handler type to update.
            identifier (Optional[str]):
                Identifier to be used in the formatter (default: existing identifier).
            identifier_max_width (Optional[int]):
                Maximum width for the identifier field (default: existing config value).
            filename_lineno_max_width (Optional[int]):
                Maximum width for filename and line number (default: existing config value).
            level_max_width (Optional[int]):
                Maximum width for the log level field (default: existing config value).
            colors (Optional[type[BaseColors]]):
                Color scheme to be used (default: existing config, ignored for file handlers).
        """
        self.config.identifier = identifier or self.config.identifier
        self.config.placement_config.placement_improvement = (
                identifier_max_width or self.config.placement_config.placement_improvement
        )
        self.config.placement_config.filename_lineno_max_width = (
                filename_lineno_max_width or self.config.placement_config.filename_lineno_max_width
        )
        self.config.placement_config.level_max_width = (
                level_max_width or self.config.placement_config.level_max_width
        )

        if hasattr(self, "logger"):
            for handler in self.logger.handlers:
                if isinstance(handler, handler_type):
                    handler.setFormatter(Formatter(
                        identifier=self.config.identifier,
                        identifier_max_width=self.config.placement_config.placement_improvement,
                        filename_lineno_max_width=self.config.placement_config.filename_lineno_max_width,
                        level_max_width=self.config.placement_config.level_max_width,
                        colors=(
                            None if handler_type is logging.FileHandler else
                            (self.config.colors if colors is None else colors)
                        ),
                    ))
                    break  # Exit loop after updating the first matching handler

    def update_print_handler_formatter(
            self,
            identifier: Optional[str] = None,
            identifier_max_width: Optional[int] = None,
            filename_lineno_max_width: Optional[int] = None,
            level_max_width: Optional[int] = None,
            colors: Optional[type[BaseColors]] = None,
            **kwargs
    ):
        """
        Updates the formatter of the StreamHandler (console logging).

        Args:
            identifier (Optional[str]): Identifier for formatting.
            identifier_max_width (Optional[int]): Max width of the identifier field.
            filename_lineno_max_width (Optional[int]): Max width for filename/line number.
            level_max_width (Optional[int]): Max width of the log level field.
            colors (Optional[type[BaseColors]]): Color scheme to be applied.
        """
        self.update_handler_formatter(
            handler_type=logging.StreamHandler,
            identifier=identifier,
            identifier_max_width=identifier_max_width,
            filename_lineno_max_width=filename_lineno_max_width,
            level_max_width=level_max_width,
            colors=colors,
        )

    def update_file_handler_formatter(
            self,
            identifier: Optional[str] = None,
            identifier_max_width: Optional[int] = None,
            filename_lineno_max_width: Optional[int] = None,
            level_max_width: Optional[int] = None,
            **kwargs
    ):
        """
        Updates the formatter of the FileHandler (file logging).

        Args:
            identifier (Optional[str]): Identifier for formatting.
            identifier_max_width (Optional[int]): Max width of the identifier field.
            filename_lineno_max_width (Optional[int]): Max width for filename/line number.
            level_max_width (Optional[int]): Max width of the log level field.
        """
        self.update_handler_formatter(
            handler_type=logging.FileHandler,
            identifier=identifier,
            identifier_max_width=identifier_max_width,
            filename_lineno_max_width=filename_lineno_max_width,
            level_max_width=level_max_width,
        )

    # ====== Logging Methods ======
    def log(self, msg: str, level: LogLevels) -> None:
        """ Logs a message at the specified log level. """
        log_func = self.log_level_to_logger_function.get(level)
        if log_func is None:
            self.logger.warning(
                f"Invalid log level [log message: {msg}]", stacklevel=2
            )
        else:
            log_func(msg, stacklevel=2)

    def fatal(self, msg: str) -> None:
        """ Logs a fatal message. """
        # 3 because the logging library doesn't support the 'fatal' level natively, so I have added it manually
        # (this added 1 to depth level)
        self.logger.fatal(msg, stacklevel=3)

    def critical(self, msg: str) -> None:
        """ Logs a critical message. """
        self.logger.critical(msg, stacklevel=2)

    def error(self, msg: str) -> None:
        """ Logs an error message. """
        self.logger.error(msg, stacklevel=2)

    def warning(self, msg: str) -> None:
        """ Logs a warning message. """
        self.logger.warning(msg, stacklevel=2)

    def info(self, msg: str) -> None:
        """ Logs an informational message. """
        self.logger.info(msg, stacklevel=2)

    def debug(self, msg: str) -> None:
        """ Logs a debug message. """
        self.logger.debug(msg, stacklevel=2)
