from abc import ABC, abstractmethod

from loggerplusplus import Logger

from strategy.core.base_game_context import BaseGameContext


class BaseTask(ABC):
    """A minimal atomic task to be executed within the strategy graph.
    Must return True when the task is complete.
    """

    def __init__(self, logger: Logger | None = None):
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )

    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool:
        pass
