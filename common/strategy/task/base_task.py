from abc import ABC, abstractmethod
from typing import Callable, List, Optional
from strategy.base_game_context import BaseGameContext


class BaseTask(ABC):
    @abstractmethod
    def handle(self, ctx: BaseGameContext) -> bool: ...
