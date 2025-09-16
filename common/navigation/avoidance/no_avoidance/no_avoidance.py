"""No-op avoidance strategy that leaves the trajectory unchanged."""

from __future__ import annotations

from typing import TYPE_CHECKING, cast

from navigation.avoidance.base_avoidance import BaseAvoidance
from navigation.avoidance.no_avoidance.no_avoidance_params import NoAvoidanceParams

if TYPE_CHECKING:
    from arena import AllyZone, EnemyZone
    from navigation.navigator.task import NavigatorTask
    from navigation.trajectory_planner import TrajectoryPlanCommand


class NoAvoidance(BaseAvoidance[NoAvoidanceParams]):
    """Implementation of a no-op avoidance strategy.

    The navigation system proceeds with its task without applying any obstacle
    avoidance logic and simply returns the current trajectory command unchanged.
    """

    @BaseAvoidance.ensure_original_task_storage
    def handle(  # noqa: PLR6301
        self,
        current_navigator_task: NavigatorTask,
        _ally_zone: AllyZone,
        _enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Handle method for no avoidance logic.

        Since this strategy does not perform any avoidance,
        it simply returns the current trajectory command as-is.

        Args:
            current_navigator_task (NavigatorTask): The current navigation task.
            _ally_zone (AllyZone): Ally zone data.
            _enemy_zone (EnemyZone): Enemy zone data.

        Returns:
            TrajectoryPlanCommand: The current trajectory command without changes.
        """
        return cast(
            "TrajectoryPlanCommand",
            current_navigator_task.current_trajectory_command,
        )
