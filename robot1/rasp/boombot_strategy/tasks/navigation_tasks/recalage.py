"""Navigation task to reach a color-reserved zone."""

from __future__ import annotations
from typing import override

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.path_planner.basic_path_planner import BasicPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)
from robot1.rasp.boombot_strategy.show_game_context import ShowGameContext
from strategy.core.tasks import BaseNavigationTask

from geometry import nearest_points, OrientedPoint


class Recalage(NavigationTask):
    """Task to recalibrate the robot's position."""

    def __init__(self, wall_dir: str = None) -> None:
        """
        Initialize the Recalage task.
        """
        self.wall_dir = wall_dir
        self.closest_wall_goal = None

        super().__init__(
            goal=None,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=40,
                width_view=30,
            ),
            stabilization_delay=2,  # change à 2 askip c'est ça
        )

    def get_closest_wall_goal(self, ctx: ShowGameContext) -> OrientedPoint:
        x, y, theta = ctx.rolling_basis.odometrie.as_tuple()
        arena_height = CONFIG.ARENA.HEIGHT
        arena_width = CONFIG.ARENA.WIDTH

        distances = {
            "top": arena_height - y,
            "bottom": y,
            "left": x,
            "right": arena_width - x,
        }

        closest_wall = min(distances, key=distances.get)

        if closest_wall == "top":
            return OrientedPoint(x, arena_height, 270)
        elif closest_wall == "bottom":
            return OrientedPoint(x, 0, 90)
        elif closest_wall == "left":
            return OrientedPoint(0, y, 0)
        elif closest_wall == "right":
            return OrientedPoint(arena_width, y, 180)

    @override
    def handle(self, ctx: ShowGameContext) -> bool:
        if not self._is_initialized:
            self._initialize(ctx)

        self.navigator_task.goal = self.get_closest_wall_goal(ctx)

        return super().handle(ctx)

