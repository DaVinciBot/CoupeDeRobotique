"""Transition implementation guarded by a runtime condition."""

from typing import override

from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.base_transition import BaseTransition
from strategy.core.transitions.conditional_transition.transitions_condition import (
    BaseTransitionCondition,
)


class ConditionalTransition(BaseTransition):
    """A transition that occurs only if a specified condition is met.

    This class allows for conditional logic when determining whether a
    transition from one task node to another is valid, using an instance of
    ``BaseTransitionCondition``.
    """

    def __init__(
        self,
        target: BaseTaskNode,
        condition: BaseTransitionCondition,
    ) -> None:
        """Initialize a conditional transition.

        Args:
            target (BaseTaskNode): The target node to transition to.
            condition (BaseTransitionCondition):
                The condition that must be met for the transition to occur.

        """
        super().__init__(target)
        self.condition = condition

    @override
    def can_transit(self, from_node: BaseTaskNode, ctx: BaseGameContext) -> bool:
        """Determine if transition can occur based on condition and context.

        Args:
            from_node (BaseTaskNode): The node transitioning from.
            ctx (BaseGameContext):
                The current game context providing necessary state for evaluation.

        Returns:
            bool:
                ``True`` if the condition is satisfied and transition can occur,
                ``False`` otherwise.

        """
        return self.condition.check(from_node, self.target, ctx)
