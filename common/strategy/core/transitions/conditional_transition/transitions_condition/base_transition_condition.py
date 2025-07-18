# ====== Code Summary ======
# This module defines an abstract base class `BaseTransitionCondition` for evaluating whether a transition
# between two task nodes is allowed within a strategy game context. It enforces the implementation of a
# `check` method in derived classes, which must determine the validity of a transition based on the
# current game context.

from abc import ABC, abstractmethod

from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode


class BaseTransitionCondition(ABC):
    """Abstract base class representing a transition condition.

    Any subclass must implement the `check` method, which determines whether a transition
    from one task node to another is permitted based on the provided game context.
    """

    @abstractmethod
    def check(
        self,
        from_node: BaseTaskNode,
        next_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> bool:
        """Evaluate whether the transition from `from_node` to `next_node` is allowed
        given the current game context.

        Args:
            from_node (BaseTaskNode): The current task node.
            next_node (BaseTaskNode): The proposed next task node.
            ctx (BaseGameContext): The context of the game which may contain state, resources, or conditions.

        Returns:
            bool: `True` if the transition is allowed, `False` otherwise.
        """
        ...
