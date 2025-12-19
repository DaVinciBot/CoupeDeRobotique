"""Provide a unified ``PIN`` interface for real or dummy GPIO access."""

from logging import Logger

from log_manager import LogLogger

_logger = LogLogger(
    identifier=__name__,
    follow_logger_manager_rules=True,
)

logger = Logger(__name__)

try:
    from gpio.gpio import PIN
except ImportError:
    logger.exception("Failed to import GPIO module")
    _logger.warning(
        "[GPIO] Failed to import GPIO module - ensure library is installed",
    )
    _logger.info("[GPIO] Falling back to dummy PIN class")
    from gpio.dummy_gpio import PIN

__all__ = ["PIN"]
