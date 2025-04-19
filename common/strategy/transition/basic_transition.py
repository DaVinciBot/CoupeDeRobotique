from __future__ import annotations

from strategy.transition.base_transition import BaseTransition
from typing import TYPE_CHECKING


from strategy.base_game_context import BaseGameContext

if TYPE_CHECKING:
    from strategy.task_node import BaseTaskNode


class BasicTransition(BaseTransition):

    def can_transit(
        self, current: BaseTaskNode, target: BaseTaskNode, ctx: BaseGameContext
    ) -> bool:
        return True
