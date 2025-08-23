# ====== Code Summary ======
# This module implements the ``DirectTransition`` class, a concrete subclass of ``BaseTransition`` that always
# allows a transition to occur unconditionally. It is used when no specific condition needs to be evaluated
# for transitioning between task nodes.


from typing import override

from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.base_transition import BaseTransition


class DirectTransition(BaseTransition):
    """A transition that is always allowed, regardless of context or state.

    This class implements the simplest form of a transition between task nodes by always
    returning ``True`` from its ``can_transit`` method.

    This is useful for default or unconditional transitions.

    """

    @override
    def can_transit(self, from_node: BaseTaskNode, ctx: BaseGameContext) -> bool:
        """Always allow the transition to occur.

        Args:
            from_node (BaseTaskNode): The current task node (unused).
            ctx (BaseGameContext): The game context (unused).

        Returns:
            bool: Always returns ``True``.

        """
        return True
