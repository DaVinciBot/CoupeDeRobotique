"""Provide a unified ``PIN`` interface for real or dummy GPIO access."""

from loggerplusplus import Logger

_logger = Logger(
    identifier=__name__,
    follow_logger_manager_rules=True,
)

try:
    from gpio.gpio import PIN
except ImportError as exc:
    _logger.warning(
        "[GPIO] Failed to import GPIO module: %s",
        exc,
    )
    _logger.info("[GPIO] Falling back to dummy PIN class")
    from gpio.dummy_gpio import PIN

__all__ = ["PIN"]
