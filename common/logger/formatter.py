# ====== Imports ======
# Standard library imports
from colorama import Fore, Back, Style
import logging
from datetime import datetime

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors import BaseColors
from logger.tools import center_and_limit


# ====== Class Part ======  
class Formatter(logging.Formatter):
    """
    Format used:
    <date(hours:min:s.ms)> -> [<identifier>] [<filename>:<line number>] <log level> | <message>
    """
    def __init__(
            self,
            identifier: str, identifier_max_width: int,
            level_max_width: int,
            colors: BaseColors = None
    ):
        self.identifier: str = identifier
        self.truncated_identifier: str = center_and_limit(identifier, identifier_max_width)

        self.level_max_width: int = level_max_width

        self.colors: BaseColors = colors

        # Create custom format for the logger
        fmt = (
            f"{self._get_date()} -> "
            f"[{self._get_identifier()}] "
            f"[{self._get_filename()}:{self._get_lineno()}] "
            f"{self._get_loglevel()} | {self._get_message()}"
        )
        self.date_format = "%H:%M:%S"

        super().__init__(fmt=fmt, datefmt=self.date_format)

    def _get_date(self) -> str:
        date: str = "%(asctime)s"
        if self.colors:
            return f"{self.colors.DATE}{date}{self.colors.RESET_ALL}"
        return date

    def _get_identifier(self) -> str:
        if self.colors:
            return f"{self.colors.IDENTIFIER}{self.truncated_identifier}{self.colors.RESET_ALL}"
        return self.truncated_identifier

    def _get_filename(self) -> str:
        filename = "%(filename)s"
        if self.colors:
            return f"{self.colors.FILENAME}{filename}{self.colors.RESET_ALL}"
        return filename

    def _get_lineno(self) -> str:
        lineno = "%(lineno)d"
        if self.colors:
            return f"{self.colors.LINENO}{lineno}{self.colors.RESET_ALL}"
        return lineno

    def _get_loglevel(self) -> str:
        return "%(levelname)s"

    def _get_message(self) -> str:
        return "%(message)s"
