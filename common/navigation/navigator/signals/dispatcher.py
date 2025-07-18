# ====== Code Summary ======
# This module defines the NavigatorSignalsDispatcher class, a robust event dispatcher
# for navigator signals using the Events library. It dynamically generates signal handlers
# based on NavigatorSignalsEnum, and provides methods to connect, disconnect, and emit signals.
# Integrated logging helps track and debug signal activity.

from collections.abc import Callable
from typing import Any

from events import Events
from loggerplusplus import Logger

from navigation.navigator.signals.signals_enum import NavigatorSignalsEnum


class NavigatorSignalsDispatcher:
    """Production-grade dispatcher for navigator signals using the Events library.

    This class dynamically creates event handlers for all defined signals in
    NavigatorSignalsEnum. It allows the connection, disconnection, and emission
    of these signals with optional arguments. Logging is used extensively for
    debugging and traceability.
    """

    def __init__(self, logger: Logger | None = None) -> None:
        """Initialize the NavigatorSignalsDispatcher.

        Dynamically creates an Events subclass with all signal names for internal use.

        Args:
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        self.logger = logger or Logger(
            identifier="NavigatorSignalsDispatcher",
            follow_logger_manager_rules=True,
        )

        # Dynamically create an Events subclass with all signal names
        event_names = tuple(signal.name for signal in NavigatorSignalsEnum)

        class NavigatorEvents(Events):
            __events__ = event_names

        self._signals = NavigatorEvents()
        self.logger.debug(
            f"NavigatorSignalsDispatcher initialized with events: {event_names}",
        )

    def connect_signal(
        self,
        signal: NavigatorSignalsEnum,
        callback: Callable[..., Any],
    ) -> None:
        """Connect a callback function to a signal.

        Args:
            signal (NavigatorSignalsEnum): The signal to connect to.
            callback (Callable[..., Any]): The callback function to attach to the signal.

        Returns:
            None
        """
        try:
            # Connect callback to signal
            event = getattr(self._signals, signal.name)
            event += callback
            self.logger.debug(f"Connected callback to signal: {signal.name}")
        except AttributeError:
            self.logger.warning(f"Attempted to connect to unknown signal: {signal}")

    def disconnect_signal(
        self,
        signal: NavigatorSignalsEnum,
        callback: Callable[..., Any],
    ) -> None:
        """Disconnect a callback function from a signal.

        Args:
            signal (NavigatorSignalsEnum): The signal to disconnect from.
            callback (Callable[..., Any]): The callback function to remove.

        Returns:
            None
        """
        try:
            # Disconnect callback from signal
            event = getattr(self._signals, signal.name)
            event -= callback
            self.logger.debug(f"Disconnected callback from signal: {signal.name}")
        except AttributeError:
            self.logger.warning(
                f"Attempted to disconnect from unknown signal: {signal}",
            )

    def emit_signal(
        self,
        signal: NavigatorSignalsEnum,
        *args,
        **kwargs,
    ) -> None:
        """Emit a signal and trigger all connected callbacks.

        Args:
            signal (NavigatorSignalsEnum): The signal to emit.
            *args: Positional arguments to pass to callbacks.
            **kwargs: Keyword arguments to pass to callbacks.

        Returns:
            None
        """
        try:
            self.logger.debug(
                f"Emitting signal: {signal.name} with args: {args}, kwargs: {kwargs}",
            )
            getattr(self._signals, signal.name)(*args, **kwargs)
        except AttributeError:
            self.logger.warning(f"Attempted to emit unknown signal: {signal}")
