"""Base class for tasks executed by the strategy system."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from log_manager import LogLogger
from strategy.core.base_game_context import BaseGameContext

if TYPE_CHECKING:
    from loggerplusplus import Logger


class BaseTask[GameContextT: BaseGameContext](ABC):
    """Atomic unit of work executed within the strategy graph."""

    def __init__(
        self,
        logger: Logger | None = None,
        points: int = 0,
        estimated_duration: float = 0.0,
    ) -> None:
        """Initialize the task.

        Args:
            logger (Logger | None): Logger instance for debugging. Defaults to None.
            points (int): Points awarded for completing this task. Defaults to 0.
            estimated_duration (float): Estimated duration of the task in seconds,
                defaults to 0.0.
        """
        self._points = points
        self._estimated_duration = estimated_duration
        self._logger: Logger = logger or LogLogger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def set_points(self, points: int) -> None:
        """Set the points awarded for completing this task.

        Args:
            points (int): The number of points for this task.
        """
        self._points = points

    @abstractmethod
    def set_estimated_duration(self, estimated_duration: float) -> None:
        """Set the estimated duration of the task in seconds.

        Args:
            estimated_duration (float): Estimated duration in seconds.
        """
        self._estimated_duration = estimated_duration

    @abstractmethod
    def estimated_duration(self) -> float:
        """Return the estimated duration of the task in seconds.

        Returns:
            float: Estimated duration in seconds.
        """
        return self._estimated_duration

    @abstractmethod
    def points(self) -> int:
        """Return the points awarded for completing this task.

        Returns:
            int: The number of points for this task.
        """
        return self._points

    @abstractmethod
    def handle(self, ctx: GameContextT) -> bool:
        """Execute the task and return ``True`` when complete.

        Args:
            ctx (GameContextT): The game context.

        Returns:
            bool: ``True`` if the task is complete, ``False`` otherwise.
        """
