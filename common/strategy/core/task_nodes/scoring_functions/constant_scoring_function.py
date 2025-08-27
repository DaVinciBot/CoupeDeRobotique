"""Scoring function returning a constant value."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class ConstantScoringFunction(BaseScoringFunction):
    """Return a fixed score regardless of context."""

    def __init__(self, score: float) -> None:
        """Store the constant score value.

        Args:
            score (float): The constant score value.

        """
        self.score: float = score

    @override
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        """Return the preset score.

        Args:
            prev_node (BaseTaskNode): The previous task node.
            current_node (BaseTaskNode): The current task node.
            ctx (BaseGameContext): The game context.

        Returns:
            float: The constant score.

        """
        return self.score
