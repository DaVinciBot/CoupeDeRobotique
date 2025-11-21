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

    def __init__(self, logger: Logger | None = None) -> None:
        """Initialize the task.

        Args:
            logger (Logger | None): Logger instance for debugging. Defaults to None.
        """
        self._logger: Logger = logger or LogLogger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def handle(self, ctx: GameContextT) -> bool:
        """Execute the task and return ``True`` when complete.

        Args:
            ctx (GameContextT): The game context.

        Returns:
            bool: ``True`` if the task is complete, ``False`` otherwise.
        """
