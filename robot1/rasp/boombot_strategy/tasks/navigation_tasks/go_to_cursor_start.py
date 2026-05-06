from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import (
    NavigationTask,
    simulation_delay,
    simulation_step_sleep_delay,
)
from geometry import OrientedPoint, distance
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.astar_path_planner import AStarPathPlannerParams
from navigation.path_planner.structs import Direction
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from rasp.boombot_strategy.winter_game_context import WinterGameContext


class GoToCursorStart(NavigationTask):
    def __init__(self, target_pos: OrientedPoint, ctx: WinterGameContext) -> None:
        super().__init__(
            goal=target_pos,
            path_planner_params=AStarPathPlannerParams(
                grid=ctx.arena.grid_manager.get_static_and_dynamic_grid(),
                path_resolution=5,
                chunk_size=CONFIG.ARENA_CHUNK_SIZE,
                start=ctx.arena.ally_zone.point,
                goal=target_pos,
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
        self.target_pos = target_pos
        self.estimated_duration = self.compute_estimated_duration

    def compute_estimated_duration(self, ctx: WinterGameContext) -> float:
        current_position: OrientedPoint = ctx.rolling_basis.odometrie
        dist: float = distance(current_position, self.target_pos)

        return (
            self.speed_profiler.linear_speed_profile.get_total_duration(
                distance=dist,
            )
            + self.stabilization_delay
        )
