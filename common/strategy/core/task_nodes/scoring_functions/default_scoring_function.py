from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class DefaultScoringFunction(BaseScoringFunction):
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        return 0.0
