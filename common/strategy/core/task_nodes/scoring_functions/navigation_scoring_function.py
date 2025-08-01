from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class NavigationScoringFunction(BaseScoringFunction):
    def __init__(self, goal: int) -> None:
        self.goal = goal

    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        distance = ctx.arena.ally_zone.point.distance(
            ctx.arena.compute_goal_position(self.goal),
        )
        return max(0.0, (1.0 - distance / 200.0) * 6.0)
