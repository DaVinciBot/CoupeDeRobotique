"""Generic maneuver tasks such as relative moves and zone centroids."""

from __future__ import annotations
from math import pi

from typing import TYPE_CHECKING, Optional

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from loggerplusplus import Logger

from geometry import OrientedPoint
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (  # noqa: E501
    RectangularProjectionAcsDetectionProfileParams,
)
from navigation.avoidance.no_avoidance import NoAvoidanceParams
from navigation.avoidance.stop_and_wait_avoidance import StopAndWaitAvoidanceParams
from navigation.navigator.task import NavigatorTask, NavigatorTaskParams
from navigation.path_planner import Direction
from navigation.path_planner.basic_path_planner import BasicPathPlannerParams
from navigation.path_planner.delta_path_planner import DeltaPathPlannerParams
from navigation.trajectory_planner.sequential_trajectory_planner import (
    SequentialTrajectoryPlannerParams,
)
from boombot_strategy.show_game_context import ShowGameContext

if TYPE_CHECKING:
    from strategy.core import BaseGameContext


class RelativeBackward(NavigationTask):
    """Navigation task to move the robot a specified distance backward."""

    def __init__(self, distance: float) -> None:
        """Initialize the RelativeBackward task.

        Args:
            distance (float): The distance to move backward in millimeters.
        """
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.BACKWARD,
                respect_goal_orientation=False,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=NoAcsDetectionProfileParams(),
            stabilization_delay=1,  # Delay to stabilize after moving backward
            timeout=20,
        )


class RelativeForward(NavigationTask):
    """Navigation task to move the robot a specified distance forward."""

    def __init__(self, distance: float) -> None:
        """Initialize the RelativeForward task.

        Args:
            distance (float): The distance to move forward in millimeters.
        """
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=NoAcsDetectionProfileParams(),
            stabilization_delay=0.5,  # Delay to stabilize after moving forward
        )


class GoCentroidOfZone(NavigationTask):
    """Navigation task to go to the centroid of a given zone."""

    def __init__(self, zone_id: int) -> None:
        """Initialize the GoCentroidOfZone task.

        Args:
            zone_id (int): The ID of the target zone.
        """
        super().__init__(
            goal=zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=2,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=0.5,
        )
        self.zone_id: int = zone_id
        self._is_initialized: bool = False
        self.navigator_task: NavigatorTask

    def _initialize(self, ctx: BaseGameContext) -> None:
        """Initialize by computing the target position from the zone centroid.

        Args:
            ctx (BaseGameContext): The game context providing arena information.
        """
        self._is_initialized = True

        # Compute the goal position with orientation
        centroid: OrientedPoint = OrientedPoint.from_point(
            ctx.arena.zones[self.zone_id].polygon.centroid,
        )

        # Create a NavigatorTask using the calculated goal
        self.navigator_task = NavigatorTask(
            params=NavigatorTaskParams(
                goal=centroid,
                timeout=self.timeout,
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            ),
        )


# TODO : A poser a Eliott → pk que arena dans basecontext peut-on ajouter rolling basis et actuators ?
class GoToClosestFreeWall(NavigationTask):
    def __init__(self) -> None:
        """
        Initialize the GoToClosestFreeWall task..
        """

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
        self.navigator_task: Optional[NavigatorTask] = None
        self.closest_wall_goal: Optional[OrientedPoint] = None

    def get_closest_wall_goal(self, ctx: ShowGameContext) -> OrientedPoint:
        """
        Determine the closest accessible wall point in the arena.

        Args:
            ctx (ShowGameContext): The game context providing arena and robot info.
        Returns:
            OrientedPoint: The closest accessible wall point.
        """
        robot_pos = ctx.rolling_basis.odometrie
        arena = ctx.arena

        arena_width = CONFIG.ARENA_WIDTH
        arena_height = CONFIG.ARENA_HEIGHT
        arena_border = CONFIG.ARENA_BORDER_BUFFER

        closest_point: OrientedPoint | None = None
        min_distance: float = float("inf")

        walls = [
            ("x", arena_border, range(0, arena_height+1), 0),
            ("x", arena_width-arena_border, range(0, arena_height+1), pi),
            ("y", arena_border, range(0, arena_width+1), -pi/2),
            ("y", arena_height-arena_border, range(0, arena_width+1), pi/2),
        ]

        for axis, fixed, var_range, orientation in walls:
            for var in var_range:
                if axis == "x":
                    candidate = OrientedPoint(fixed, var, orientation)
                else:
                    candidate = OrientedPoint(var, fixed, orientation)

                zone = arena.get_zone_by_location(candidate)
                if zone is None:
                    continue
                if zone not in arena.find_zone_accessibility("FREE"):
                    continue

                dx = candidate.x - robot_pos.x
                dy = candidate.y - robot_pos.y
                distance = (dx ** 2 + dy ** 2) ** 0.5

                if distance < min_distance:
                    min_distance = distance
                    closest_point = candidate

        return closest_point

    def _initialize(self, ctx: ShowGameContext) -> None:
        """Initialize the recalage task by determining the closest wall goal."""

        goal = self.get_closest_wall_goal(ctx)

        self.closest_wall_goal = goal

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
        self._is_initialized = True

