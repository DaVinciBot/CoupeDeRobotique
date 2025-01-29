# TODO: implémenter un cleaner de log qui supprime les logs de la qui date de plus de 7 jours par exmeple
# TODO: faire aussi un cleaner de log du fichier du jour afin de ne pas avoir par exmpele plus de 1000000 de ligne
# TODO: à l'improt du logger pourquoi pas affichier la taille qu'occupe klez fichiers de logs trouvé actuellemnt en ko

# ====== Code Summary ======
# This module enhances Python's built-in logging by adding a distinct 'FATAL' log level,
# improving log formatting, and enabling color-coded log messages for better readability.
# It provides a custom Logger class that supports console and file logging with adjustable
# color settings, ensuring clear and structured log outputs.

# ====== Imports ======
# Standard library imports
import datetime
import logging
import sys
import os

# Third-party library imports
from colorama import just_fix_windows_console

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors import BaseColors
from logger.formatter import Formatter

# ====== Initialize Console for Colors ======
just_fix_windows_console()  # Enables colors in windows consoles (why not)

# ====== Modification of Native Logging Behavior ======
# Python's logging module treats 'CRITICAL' and 'FATAL' as synonyms.
# To distinguish 'FATAL' as a unique severity level, we manually add it.
logging.addLevelName(LogLevels.FATAL, "FATAL")


# Define a method for the Logger class to log messages at 'FATAL' level.
def class_fatal(self, msg, *args, **kwargs):
    """
    Log 'msg % args' with severity 'FATAL'.

    To pass exception information, use the keyword argument exc_info with
    a true value, e.g.

    This allows using `logger.fatal()` as a distinct logging level.

    logger.fatal("Houston, we have one %s", "major disaster", exc_info=True)

    Args:
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

    def __init__(
            self,
            identifier: str = "unknown",
            decorator_log_level: LogLevels = LogLevels.DEBUG,
            print_log_level: LogLevels = LogLevels.DEBUG,
            file_log_level: LogLevels = LogLevels.DEBUG,
            print_log: bool = True,
            write_to_file: bool = True,
            colors: type[BaseColors] = None,
            identifier_max_width: int = 0,
            level_max_width: int = 0,
            filename_lineno_max_width: int = 15,
            placement_improvement: bool = True,
            path: str = "logs",
    ):
        """
        Initializes a Logger instance.

        Args:
            identifier (str): Logger name.
            decorator_log_level (LogLevels): Minimum level for decorator logs.
            print_log_level (LogLevels): Minimum level for console logs.
            file_log_level (LogLevels): Minimum level for file logs.
            print_log (bool): Whether to log to console.
            write_to_file (bool): Whether to log to a file.
            colors (type[BaseColors]): Color settings for console output.
            identifier_max_width (int): Max width for log source identifier.
            level_max_width (int): Max width for log level label.
            filename_lineno_max_width (int): Max width for filename + line number.
            placement_improvement (bool): Whether to adjust text alignment.
            path (str): Directory path for log files.
        """
        logger_already_exists = identifier in logging.root.manager.loggerDict
        if logger_already_exists:
            self.logger = logging.getLogger(identifier)
        else:
            self.logger: logging.Logger = logging.getLogger(identifier)
            self.logger.setLevel(LogLevels.DEBUG)

        # Log levels
        self.decorator_level: LogLevels = decorator_log_level
        self.print_log_level: LogLevels = print_log_level
        self.file_log_level: LogLevels = file_log_level

        # Determine max widths for alignment
        if identifier_max_width == 0:
            identifier_max_width = len(identifier) + (2 if placement_improvement else 0)
        if level_max_width == 0:
            level_max_width = max(len(level.name) for level in LogLevels) + (2 if placement_improvement else 0)

        # Define log file path
        if write_to_file and not logger_already_exists:
            if not os.path.isdir(path):
                os.mkdir(path)
            self.full_path = os.path.join(path, f"{datetime.datetime.now().strftime('%Y-%m-%d')}.log")

        # Console logging setup
        if print_log and not logger_already_exists:
            self.print_formatter: Formatter = Formatter(
                identifier=identifier,
                identifier_max_width=identifier_max_width,
                filename_lineno_max_width=filename_lineno_max_width,
                level_max_width=level_max_width,
                colors=colors,
            )

            self.console_handler = logging.StreamHandler(stream=sys.stdout)
            self.console_handler.setFormatter(self.print_formatter)
            self.console_handler.setLevel(print_log_level)

            self.logger.addHandler(self.console_handler)

        # File logging setup
        if write_to_file and not logger_already_exists:
            self.file_formatter: Formatter = Formatter(
                identifier=identifier,
                identifier_max_width=identifier_max_width,
                filename_lineno_max_width=filename_lineno_max_width,
                level_max_width=level_max_width,
                colors=None
            )

            self.file_handler = logging.FileHandler(filename=self.full_path)
            self.file_handler.setFormatter(self.file_formatter)
            self.file_handler.setLevel(file_log_level)

            self.logger.addHandler(self.file_handler)

        # Map log levels to logger methods
        self.log_level_to_logger_function = {
            LogLevels.FATAL: self.logger.fatal,
            LogLevels.CRITICAL: self.logger.critical,
            LogLevels.ERROR: self.logger.error,
            LogLevels.WARNING: self.logger.warning,
            LogLevels.INFO: self.logger.info,
            LogLevels.DEBUG: self.logger.debug,
        }

    # ====== Logging Methods ======
    def log(self, msg: str, level: LogLevels) -> None:
        """ Logs a message at the specified log level. """
        self.log_level_to_logger_function.get(
            level,
            lambda bind_msg, stack_level: self.logger.warning(
                msg=f"Invalid log level [log message: {bind_msg}]", stacklevel=stack_level
            ),
        )(msg, stacklevel=2)

    def fatal(self, msg: str) -> None:
        """ Logs a fatal message. """
        self.logger.fatal(msg, stacklevel=2)

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
