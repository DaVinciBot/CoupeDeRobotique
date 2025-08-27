"""Base class for tasks executed by the strategy system."""

from abc import ABC, abstractmethod

from loggerplusplus import Logger

from strategy.core.base_game_context import BaseGameContext


class BaseTask(ABC):
    """Atomic unit of work executed within the strategy graph."""

    def __init__(self, logger: Logger | None = None) -> None:
        """Initialize the task.

        Args:
            logger (Logger | None): Logger instance for debugging. Defaults to None.

        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool:
        """Execute the task and return ``True`` when complete.

        Args:
            ctx (BaseGameContext): The game context.

        Returns:
            bool: ``True`` if the task is complete, ``False`` otherwise.

        """
