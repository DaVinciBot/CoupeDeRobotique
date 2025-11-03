"""Dispatcher managing navigator signals using the Events library."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from events import Events
from loggerplusplus import Logger

from navigation.navigator.signals.signals_enum import NavigatorSignalsEnum

if TYPE_CHECKING:
    from collections.abc import Callable


class NavigatorSignalsDispatcher:  # UNUSED
    """Dispatcher for navigator signals."""

    def __init__(self, logger: Logger | None = None) -> None:
        """Initialize the NavigatorSignalsDispatcher.

        Dynamically creates an Events subclass with all signal names for internal use.

        Args:
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to None.
        """
        self._logger = logger or Logger(
            identifier="NavigatorSignalsDispatcher",
            follow_logger_manager_rules=True,
        )

        # Dynamically create an Events subclass with all signal names
        event_names = tuple(signal.name for signal in NavigatorSignalsEnum)

        class NavigatorEvents(Events):
            """Dynamic Events subclass for navigator signals."""

            __events__ = event_names

        self._signals = NavigatorEvents()
        self._logger.debug(
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
            callback (Callable[..., Any]):
                The callback function to attach to the signal.
        """
        try:
            # Connect callback to signal
            event = getattr(self._signals, signal.name)
            event += callback
            self._logger.debug(f"Connected callback to signal: {signal.name}")
        except AttributeError:
            self._logger.warning(f"Attempted to connect to unknown signal: {signal}")

    def disconnect_signal(
        self,
        signal: NavigatorSignalsEnum,
        callback: Callable[..., Any],
    ) -> None:
        """Disconnect a callback function from a signal.

        Args:
            signal (NavigatorSignalsEnum): The signal to disconnect from.
            callback (Callable[..., Any]): The callback function to remove.
        """
        try:
            # Disconnect callback from signal
            event = getattr(self._signals, signal.name)
            event -= callback
            self._logger.debug(f"Disconnected callback from signal: {signal.name}")
        except AttributeError:
            self._logger.warning(
                f"Attempted to disconnect from unknown signal: {signal}",
            )

    def emit_signal(  # UNUSED
        self,
        signal: NavigatorSignalsEnum,
        *args: Any,  # noqa: ANN401
        **kwargs: Any,  # noqa: ANN401
    ) -> None:
        """Emit a signal and trigger all connected callbacks.

        Args:
            signal (NavigatorSignalsEnum): The signal to emit.
            *args(Any): Positional arguments to pass to callbacks.
            **kwargs(Any): Keyword arguments to pass to callbacks.
        """
        try:
            self._logger.debug(
                f"Emitting signal: {signal.name} with args: {args}, kwargs: {kwargs}",
            )
            getattr(self._signals, signal.name)(*args, **kwargs)
        except AttributeError:
            self._logger.warning(f"Attempted to emit unknown signal: {signal}")
