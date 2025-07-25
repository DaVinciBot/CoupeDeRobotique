# ====== Code Summary ======
# This module implements the ``FromFunctionTransitionCondition`` class, which inherits from the
# ``BaseTransitionCondition`` abstract base class. It allows defining custom transition conditions
# using a user-provided function. The function determines if a transition between task nodes is allowed,
# based on the current game context.

from collections.abc import Callable

from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.conditional_transition.transitions_condition.base_transition_condition import (
    BaseTransitionCondition,
)


class FromFunctionTransitionCondition(BaseTransitionCondition):
    """A transition condition that delegates its logic to a user-provided function.

    This class enables flexible, reusable logic for determining transitions between task nodes
    by passing a function during instantiation. The function is expected to return a boolean
    indicating whether the transition should be allowed.
    """

    def __init__(
        self,
        func: Callable[[BaseTaskNode, BaseTaskNode, BaseGameContext], bool],
    ) -> None:
        """Initialize the transition condition with a custom function.

        Args:
            func (Callable[[BaseTaskNode, BaseTaskNode, BaseGameContext], bool]): A function that defines the logic for transition validation.
        """
        self.func = func

    def check(
        self,
        from_node: BaseTaskNode,
        next_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> bool:
        """Check whether the transition is valid using the provided function.

        Args:
            from_node (BaseTaskNode): The current task node.
            next_node (BaseTaskNode): The proposed next task node.
            ctx (BaseGameContext): The current game context.

        Returns:
            bool: ``True`` if the transition is allowed according to the provided function, ``False`` otherwise.
        """
        return self.func(from_node, next_node, ctx)
