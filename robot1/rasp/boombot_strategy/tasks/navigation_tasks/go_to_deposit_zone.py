"""Navigation task to reach a color-reserved zone."""

from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from geometry import OrientedPoint, distance
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.basic_path_planner import BasicPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from rasp.boombot_strategy.winter_game_context import WinterGameContext


class GoToDepositZone(NavigationTask):
    """Task to navigate to a deposit zone."""

    def __init__(self, deposit_zone_id: int) -> None:
        """Initialize the GoToColorReservedZoneToConstruct task.

        Args:
            deposit_zone_id (int): The ID of the target zone.
        """
        super().__init__(
            goal=deposit_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=1,  # Delay to stabilize before construction
            points=0,
        )
        self.zone_id: int = deposit_zone_id
        self.estimated_duration = self.compute_estimated_duration

    def compute_estimated_duration(self, ctx: WinterGameContext) -> float:
        """Estimate duration based on distance to the target color reserved zone.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            float: Estimated time to reach the color reserved zone in seconds.
        """
        centroid: OrientedPoint = OrientedPoint.from_point(
            ctx.arena.zones[self.zone_id].polygon.centroid,
        )
        dist: float = float(distance(centroid, ctx.arena.ally_zone.point))
        return (
            self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=dist,
            )
            + self.stabilization_delay
        )
