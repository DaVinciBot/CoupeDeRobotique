"""Scoring based on distance to a navigation goal."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class NavigationScoringFunction(BaseScoringFunction):
    """Score nodes higher the closer the robot is to a goal."""

    def __init__(self, goal: int) -> None:
        """Initialize the navigation scoring function.

        Args:
            goal (int): The navigation goal to reach.

        """
        self.goal = goal

    @override
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        """Compute the navigation score based on distance to the goal.

        Args:
            prev_node (BaseTaskNode): The previous task node.
            current_node (BaseTaskNode): The current task node.
            ctx (BaseGameContext): The game context.

        Returns:
            float: The computed navigation score.

        """
        distance = ctx.arena.ally_zone.point.distance(
            ctx.arena.compute_goal_position(self.goal),
        )
        return max(0.0, (1.0 - distance / 200.0) * 6.0)
