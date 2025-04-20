from __future__ import annotations
from abc import ABC, abstractmethod
from strategy.base_game_context import BaseGameContext


from typing import TYPE_CHECKING


from strategy.base_game_context import BaseGameContext

if TYPE_CHECKING:
    from strategy.task_node import BaseTaskNode


class BaseTransition(ABC):
    def __init__(self, target: BaseTaskNode):
        self.target = target

    @abstractmethod
    def can_transit(
        self, current: BaseTaskNode, target: BaseTaskNode, ctx: BaseGameContext
    ) -> bool: ...
