from abc import ABC, abstractmethod
from strategy.core.base_game_context import BaseGameContext


class BaseTask(ABC):
    """
    A minimal atomic task to be executed within the strategy graph.
    Must return True when the task is complete.
    """

    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool:
        pass
