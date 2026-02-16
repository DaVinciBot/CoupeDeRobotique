from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from geometry import OrientedPoint, distance
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.basic_path_planner import BasicPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)

if TYPE_CHECKING:
    from rasp.boombot_strategy.winter_game_context import WinterGameContext


class GoToCursorStart(NavigationTask):

    def __init__(self, target_pos: OrientedPoint) -> None:
        super().__init__(
            goal=target_pos,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=1,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50,
                width_view=40,
            ),
            stabilization_delay=0.5,
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
