"""Abstract interfaces for conditions used by conditional transitions."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseTransitionCondition(ABC):
    """Abstract base class representing a transition condition.

    Any subclass must implement the ``check`` method, which determines whether a
    transition from one task node to another is permitted based on the provided
    game context.

    """

    @abstractmethod
    def check(
        self,
        from_node: BaseTaskNode,
        next_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> bool:
        """Evaluate whether the transition is allowed given the current game context.

        Args:
            from_node (BaseTaskNode): The current task node.
            next_node (BaseTaskNode): The proposed next task node.
            ctx (BaseGameContext): The context of the game which may contain state,
                resources, or conditions.

        Returns:
            bool: ``True`` if the transition is allowed, ``False`` otherwise.

        """
