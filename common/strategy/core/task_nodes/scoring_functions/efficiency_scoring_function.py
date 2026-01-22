"""Score based on efficiency (point gain and time taken) with a k factor to balance."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class EfficiencyScoringFunction(BaseScoringFunction):
    """Score high for efficient task completion."""

    def __init__(self, k: float = 0.5) -> None:
        """Initialize the efficiency scoring function.

        Args:
            k (float): Balancing factor between points and time. Defaults to 1.0.
        """
        self.k = k

    @override
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        """Compute the efficiency score between point gain and time taken.

        Args:
            prev_node (BaseTaskNode): _description_
            current_node (BaseTaskNode): _description_
            ctx (BaseGameContext): _description_

        Returns:
            float: _description_
        """
        return self.k * current_node.points + (1 - self.k) * (
            1 / (current_node.estimated_duration + 1e-5)  # Avoid division by zero
        )
