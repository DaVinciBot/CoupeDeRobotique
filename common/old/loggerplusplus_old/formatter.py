# ====== Code Summary ======
# This module provides a custom logging formatter that ensures proper time formatting,
# applies customizable log message formatting, and supports colorized log output.
# It extends Python's logging.Formatter and introduces dynamic formatting features
# based on log level, filename, and user-defined settings.

# ====== Imports ======
# Standard library imports
import logging
import datetime

# Internal project imports
from logger.tools import center_and_limit
from logger.log_levels import LogLevels
from logger.colors import BaseColors


# ====== Class Part ======
class TimeFormatter(logging.Formatter):
    """
    Intermediate class that properly handles %f to display milliseconds with 3 digits.
    Retains the '.' as a separator.
    """

    def formatTime(self, record: logging.LogRecord, date_format: str = None) -> str:
        """
        Formats the timestamp of a log record.

        Args:
            record (logging.LogRecord): The log record containing the timestamp.
            date_format (str, optional): The date format string. Defaults to None.

        Returns:
            str: Formatted timestamp.
        """
        t = datetime.datetime.fromtimestamp(record.created)

        if date_format and "%f" in date_format:
            # Convert microseconds to milliseconds (3 digits)
            return t.strftime(date_format).replace("%f", f"{record.msecs:03.0f}")

        return super().formatTime(record, date_format)


class Formatter(TimeFormatter):
    """
    Custom log formatter that applies structured formatting with optional colors.

    Format:
    <date(hours:min:s.ms)> -> [<identifier>] [<filename>:<line number>] <log level> | <message>
    """

    def __init__(
            self,
            identifier: str,
            identifier_max_width: int,
            filename_lineno_max_width: int,
            level_max_width: int,
            colors: type[BaseColors] = None,
    ):
        """
        Initializes the Formatter with specified settings.

        Args:
            identifier (str): Identifier for the log.
            identifier_max_width (int): Maximum width for identifier display.
            filename_lineno_max_width (int): Max width for filename + line number.
            level_max_width (int): Max width for log level.
            colors (BaseColors, optional): Color settings. Defaults to None.
        """
        self.identifier = identifier
        self.truncated_identifier = center_and_limit(identifier, identifier_max_width)
        self.filename_lineno_max_width = filename_lineno_max_width
        self.level_max_width = level_max_width
        self.colors = colors
        self.evaluated_log_level = self._evaluate_log_level()
        self.date_format = "%H:%M:%S.%f"

        # Create custom format for the logger
        fmt = self._get_fmt()
        super().__init__(fmt=fmt, datefmt=self.date_format)

    def _evaluate_log_level(self) -> dict[str, str]:
        """
        Evaluates and formats log levels with optional color.

        Returns:
            dict[str, str]: Dictionary mapping log levels to formatted strings.
        """
        evaluated_log_level = {}
        for level in LogLevels:
            formatted_level = center_and_limit(level.name, self.level_max_width)
            evaluated_log_level[level.name] = (
                f"{self.colors.get_log_level_color(level)}{formatted_level}{self.colors.RESET_ALL}"
                if self.colors else formatted_level
            )
        return evaluated_log_level

    def _get_fmt(self) -> str:
        """
        Constructs the log format string.

        Returns:
            str: Log format string.
        """
        return (
            f"{self._get_date()} -> "
            f"[{self._get_identifier()}] "
            f"[{self._get_filename()}:{self._get_lineno()}] "
            f"{self._get_loglevel()} | {self._get_message()}"
        )

    def _get_date(self) -> str:
        date = "%(asctime)s"
        return f"{self.colors.DATE}{date}{self.colors.RESET_ALL}" if self.colors else date

    def _get_identifier(self) -> str:
        return (
            f"{self.colors.IDENTIFIER}{self.truncated_identifier}{self.colors.RESET_ALL}"
            if self.colors
            else self.truncated_identifier
        )

    def _get_filename(self) -> str:
        filename = "%(filename)s"
        return f"{self.colors.FILENAME}{filename}{self.colors.RESET_ALL}" if self.colors else filename

    def _get_lineno(self) -> str:
        lineno = "%(lineno)s"
        return f"{self.colors.LINENO}{lineno}{self.colors.RESET_ALL}" if self.colors else lineno

    @staticmethod
    def _get_loglevel() -> str:
        return "%(custom_levelname)s"

    @staticmethod
    def _get_message() -> str:
        return "%(message)s"

    def _get_dynamic_levelname(self, level: str) -> str:
        """
        Retrieves the formatted log level name.

        Args:
            level (str): Log level name.

        Returns:
            str: Formatted log level string.
        """
        return self.evaluated_log_level.get(level, f"ERROR UNKNOWN LOG LEVEL [{level}]")

    def _get_dynamic_message(self, message: str) -> str:
        """
        Applies color formatting to the log message if enabled.

        Args:
            message (str): Log message.

        Returns:
            str: Formatted message.
        """
        return f"{self.colors.MESSAGE}{message}{self.colors.RESET_ALL}" if self.colors else message

    def _get_dynamic_filename(self, filename: str, lineno: str) -> str:
        """
        Truncates filename if necessary to fit within max width constraints.

        Args:
            filename (str): Filename of the log origin.
            lineno (str): Line number as a string.

        Returns:
            str: Adjusted filename.
        """
        width_limit = self.filename_lineno_max_width - len(lineno)
        return center_and_limit(text=filename, width=width_limit)

    def format(self, record: logging.LogRecord) -> str:
        """
        Formats a logging record using the custom formatter.

        Args:
            record (logging.LogRecord): The log record to format.

        Returns:
            str: The formatted log message.
        """
        record.filename = self._get_dynamic_filename(record.filename, str(record.lineno))
        record.custom_levelname = self._get_dynamic_levelname(record.levelname)
        record.message = self._get_dynamic_message(record.msg)
        return super().format(record)
