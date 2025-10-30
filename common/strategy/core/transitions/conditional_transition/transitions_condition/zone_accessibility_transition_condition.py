"""Transition condition checking if a zone is accessible for the team."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any, override

from strategy.core.tasks import BaseNavigationTask
from strategy.core.transitions.conditional_transition.transitions_condition.base_transition_condition import (  # noqa: E501
    BaseTransitionCondition,
)

if TYPE_CHECKING:
    from arena.base_arena.arena_zones.base_arena_zone import BaseArenaZone
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.base_task_node import BaseTaskNode


class ZoneAccessibilityTransitionCondition(BaseTransitionCondition):
    """Check whether a specific arena zone is accessible.

    This condition is fulfilled if the designated zone is accessible to the
    current team. An optional reverse flag allows inverting the condition to
    check for inaccessibility.
    """

    def __init__(self, *, reverse: bool = False) -> None:
        """Initialize the condition with optional reversal.

        Args:
            reverse (bool, optional):
                Whether to reverse the condition logic. Defaults to ``False``.
        """
        self.reverse = reverse

    @override
    def check(
        self,
        from_node: BaseTaskNode,
        next_node: BaseTaskNode,
        ctx: BaseGameContext,
    ) -> bool:
        """Determine if the transition is allowed based on zone accessibility.

        Args:
            from_node (BaseTaskNode): The current task node.
            next_node (BaseTaskNode): The proposed next task node.
            ctx (BaseGameContext):
                The game context, including arena and team information.

        Returns:
            bool:
                ``True`` if the condition is met (zone is accessible or not based
                on ``reverse``), ``False`` otherwise.
        """
        navigation_tasks: list[BaseNavigationTask[Any]] = [
            task for task in next_node.tasks if isinstance(task, BaseNavigationTask)
        ]
        if not navigation_tasks:
            return not self.reverse

        goals: list[BaseArenaZone] = [
            zone
            for task in navigation_tasks
            if task.goal is not None
            for zone in [ctx.arena.get_zone_by_location(task.goal)]
            if zone is not None
        ]
        accessibility: bool = all(
            zone.is_accessible(team_color=ctx.arena.team_color) for zone in goals
        )

        return self.reverse ^ accessibility
