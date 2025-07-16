# ====== Code Summary ======
# This module implements the `ZoneAccessibilityTransitionCondition` class, a concrete subclass of
# `BaseTransitionCondition`. It determines whether a transition between task nodes is allowed based
# on the accessibility of a specific zone within the arena. The condition can be reversed if needed.


from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.transitions.conditional_transition.transitions_condition.base_transition_condition import (
    BaseTransitionCondition,
)


class ZoneAccessibilityTransitionCondition(BaseTransitionCondition):
    """A transition condition that checks the accessibility of a specific zone in the arena.

    This condition is fulfilled if the designated zone is accessible to the current team.
    An optional reverse flag allows inverting the condition to check for inaccessibility.

    Attributes:
        zone_id (int): The ID of the zone to check.
        reverse (bool): If True, the condition is fulfilled when the zone is NOT accessible.
    """

    def __init__(self, zone_id: int, reverse: bool = False):
        """Initialize the condition with a specific zone ID and optional reversal.

        Args:
            zone_id (int): The identifier of the zone whose accessibility will be checked.
            reverse (bool, optional): Whether to reverse the condition logic. Defaults to False.
        """
        self.zone_id = zone_id
        self.reverse = reverse

    def check(
        self, from_node: BaseTaskNode, next_node: BaseTaskNode, ctx: BaseGameContext,
    ) -> bool:
        """Determine if the transition is allowed based on zone accessibility.

        Args:
            from_node (BaseTaskNode): The current task node.
            next_node (BaseTaskNode): The proposed next task node.
            ctx (BaseGameContext): The game context, including arena and team information.

        Returns:
            bool: True if the condition is met (zone is accessible or not based on `reverse`), False otherwise.
        """
        accessibility: bool = ctx.arena.zones[self.zone_id].is_accessible(
            team_color=ctx.arena.team_color,
        )

        # If reverse is True, invert the accessibility condition
        if self.reverse:
            return not accessibility
        return accessibility
