"""Fallback scoring that always returns zero."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class DefaultScoringFunction(BaseScoringFunction):
    """Return zero for all nodes, serving as a neutral default."""

    @override
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        """Always return ``0.0``.

        Args:
            prev_node (BaseTaskNode): The previous task node.
            current_node (BaseTaskNode): The current task node.
            ctx (BaseGameContext): The game context.

        Returns:
            float: Always returns ``0.0``.

        """
        return 0.0
