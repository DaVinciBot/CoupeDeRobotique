"""Navigation task to reach a color-reserved zone."""

from __future__ import annotations
from typing import override, Optional

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.navigator.task import NavigatorTaskParams, NavigatorTask
from navigation.path_planner.basic_path_planner import BasicPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)
from robot1.rasp.boombot_strategy.show_game_context import ShowGameContext
from strategy.core.tasks import BaseNavigationTask

from geometry import nearest_points, OrientedPoint
from loggerplusplus import Logger


class Recalage(NavigationTask):
    """Task to recalibrate the robot's position by going to the closest wall."""

    def __init__(self, wall_dir: str = None, logger: Logger = None) -> None:
        self.wall_dir = wall_dir
        self.closest_wall_goal: Optional[OrientedPoint] = None
        self.logger = logger

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
            stabilization_delay=2,
        )

        self._is_initialized = False

    def get_closest_wall_goal(self, ctx: ShowGameContext) -> OrientedPoint:
        pos = ctx.rolling_basis.odometrie
        arena_height = CONFIG.ARENA_HEIGHT
        arena_width = CONFIG.ARENA_WIDTH
        distances = {
            "top": arena_height - pos.y,
            "bottom": pos.y,
            "left": pos.x,
            "right": arena_width - pos.x,
        }

        closest_wall = min(distances, key=distances.get)

        if closest_wall == "top":
            return OrientedPoint(pos.x, arena_height, 270)
        elif closest_wall == "bottom":
            return OrientedPoint(pos.x, 0, 90)
        elif closest_wall == "left":
            return OrientedPoint(0, pos.y, 0)
        else:
            return OrientedPoint(arena_width, pos.y, 180)

    def _initialize(self, ctx: ShowGameContext) -> None:
        """Initialize the recalage task by determining the closest wall goal."""

        self._is_initialized = True

        goal = self.get_closest_wall_goal(ctx)
        self.closest_wall_goal = goal
        self.logger.debug(f"Recalage towards wall at {goal}")

        params = NavigatorTaskParams(
            goal=goal,
            timeout=getattr(self, "timeout", None),
            path_planner_params=self.path_planner_params,
            trajectory_planner_params=self.trajectory_planner_params,
            speed_profiler=self.speed_profiler,
            avoidance_params=self.avoidance_params,
            acs_detection_profile_params=self.acs_detection_profile_params,
            stabilization_delay=self.stabilization_delay,
        )

        self.navigator_task = NavigatorTask(params=params)
