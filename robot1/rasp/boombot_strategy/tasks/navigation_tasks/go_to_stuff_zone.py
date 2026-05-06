"""Navigation task directing the robot to a stuff zone for pickup."""

from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import (
    NavigationTask,
    simulation_delay,
    simulation_step_sleep_delay,
)
from geometry import OrientedPoint, distance
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.astar_path_planner import AStarPathPlannerParams
from navigation.path_planner.structs import Direction
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from rasp.boombot_strategy import WinterGameContext


class GoToStuffZoneToPickUp(NavigationTask):
    """Navigate the robot to a specified stuff zone for a pickup.

    Configures path planning, trajectory planning, speed profiling, and
    avoidance strategies. Uses a rectangular projection ACS detection profile to
    avoid collisions and applies a stabilization delay for system readiness
    before performing tasks.
    """

    def __init__(self, stuff_zone_id: int, ctx: WinterGameContext) -> None:
        """Initialize navigation and avoidance parameters.

        Args:
            stuff_zone_id (int): Identifier for the target stuff zone location.
            ctx (WinterGameContext): The current game context.

        Raises:
            ValueError: If the provided color_reserved_zone_id is invalid.
        """
        goal = ctx.arena.compute_goal_position(stuff_zone_id)

        if goal is None:
            msg = f"Invalid stuff zone ID: {stuff_zone_id}"
            raise ValueError(msg)

        super().__init__(
            goal=goal,
            path_planner_params=AStarPathPlannerParams(
                grid=ctx.arena.grid_manager.get_static_and_dynamic_grid(),
                path_resolution=5,
                chunk_size=CONFIG.ARENA_CHUNK_SIZE,
                start=ctx.arena.ally_zone.point,
                goal=goal,
                direction=Direction.FORWARD,
            ),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=simulation_step_sleep_delay(2),
            ),
            # Use for pickup speed profiler
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=simulation_delay(2),
            points=0,
        )
        self.zone_id: int = stuff_zone_id
        self.estimated_duration = self.compute_estimated_duration

    def compute_estimated_duration(self, ctx: WinterGameContext) -> float:
        """Estimate duration based on distance to the target stuff zone.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            float: Estimated time to reach the stuff zone in seconds.
        """
        target_point: OrientedPoint = OrientedPoint.from_point(
            ctx.arena.zones[self.zone_id].polygon.centroid,
        )
        current_position: OrientedPoint = ctx.rolling_basis.odometrie
        dist: float = distance(current_position, target_point)

        return (
            self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=dist,
            )
            + self.stabilization_delay
        )
