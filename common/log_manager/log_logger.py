"""LogLogger class extending Logger to set up custom logging handlers."""

import logging
import sys
from typing import override

from loggerplusplus import Logger


class LogLogger(Logger):
    """Custom Logger that sets up additional DB handler."""

    @override
    def _setup_handlers(self) -> None:
        """Sets up logging handlers for console and file output."""
        if self.config.log_levels_config.print_log:
            self._set_handler(
                logging.StreamHandler(stream=sys.stdout),
                self.config.log_levels_config.print_log_level,
                self.config.colors,
            )
        if self.config.log_levels_config.write_to_file:
            self._set_handler(
                logging.FileHandler(self.config.full_path),
                self.config.log_levels_config.file_log_level,
                colors=None,
            )
