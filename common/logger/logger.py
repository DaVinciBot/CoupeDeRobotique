# ====== Imports ======
# Standard library imports
import logging

# Internal project imports
from logger.log_levels import LogLevels
from logger.colors import BaseColors

# ====== Class Part ======
class Logger:
    def __init__(
            self,
            identifier: str = "unknown",
            decorator_log_level: LogLevels = LogLevels.DEBUG,
            print_log_level: LogLevels = LogLevels.INFO,
            file_log_level: LogLevels = LogLevels.DEBUG,
            print_log: bool = True,
            write_to_file: bool = True,
    ):
        self.logger: logging.Logger = logging.getLogger(identifier)

        # Levels
        self.decorator_level: LogLevels = decorator_log_level
        self.print_log_level: LogLevels = print_log_level
        self.file_log_level: LogLevels = file_log_level

        # print logging
        if print_log:
            self.print_formatter: logging.Formatter = logging.Formatter(
                "%(asctime)s -> [] | %(levelname)s  %(message)s"
            )

        formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")

        file_handler = logging.FileHandler("logs.txt")
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)

        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        console_handler.setLevel(logging.INFO)
