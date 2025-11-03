"""Provide a unified ``PIN`` interface for real or dummy GPIO access."""

from loggerplusplus import Logger

_logger = Logger(
    identifier=__name__,
    follow_logger_manager_rules=True,
)

try:
    from gpio.gpio import PIN
except ImportError:
    _logger.warning(
        "Failed to import GPIO module. "
        "Ensure the GPIO library is installed and accessible.",
    )
    _logger.info("Falling back to dummy PIN class.")
    from gpio.dummy_gpio import PIN

__all__ = ["PIN"]
