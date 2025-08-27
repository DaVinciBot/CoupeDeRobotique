"""Interfaces for scoring how desirable a task node is."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseScoringFunction(ABC):
    """Protocol for computing scores used in node selection."""

    @abstractmethod
    def compute(
        self,
        prev_node: BaseTaskNode,
        current_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> float:
        """Compute a score for the current node based on the previous node and context.

        Args:
            prev_node (BaseTaskNode): The entry node.
            current_node (BaseTaskNode): The current node.
            ctx (BaseGameContext): The game context.

        Returns:
            float: The computed score.

        """
