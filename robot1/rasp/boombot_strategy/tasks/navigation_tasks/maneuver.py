"""Generic maneuver tasks such as relative moves and zone centroids."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
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

    @override
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
