from __future__ import annotations

from strategy.transition.base_transition import BaseTransition
from typing import TYPE_CHECKING, Callable


from strategy.base_game_context import BaseGameContext

if TYPE_CHECKING:
    from strategy.task_node import BaseTaskNode


class ConditionalTransition(BaseTransition):

    def __init__(
        self,
        target: BaseTaskNode,
        condition: Callable[[BaseTaskNode, BaseTaskNode, BaseGameContext], bool],
    ) -> None:
        super().__init__(target)
        self.condition = condition

    def can_transit(
        self, current: BaseTaskNode, target: BaseTaskNode, ctx: BaseGameContext
    ) -> bool:
        return self.condition(current, target, ctx)
