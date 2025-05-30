# ====== Code Summary ======
# This module defines three specialized navigation tasks:
# - `RelativeBackward`: Moves the robot a specified distance backward.
# - `RelativeForward`: Moves the robot a specified distance forward.
# - `GoCentroidOfZone`: Navigates the robot to the centroid of a specified arena zone,
#   initializing a navigator task with customized planning and avoidance parameters.

# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation import (
    DeltaPathPlannerParams,
    NoAvoidanceParams,
    SequentialTrajectoryPlannerParams,
    Direction,
    BasicPathPlannerParams,
    StopAndWaitAvoidanceParams,
    NavigatorTaskParams,
    NavigatorTask,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfileParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)
from strategy.core import BaseGameContext
from geometry import OrientedPoint, Point


class RelativeBackward(NavigationTask):
    """
    Navigation task to move the robot a specified distance backward.

    Args:
        distance (float): The distance to move backward in millimeters.
    """

    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.BACKWARD,
                respect_goal_orientation=False
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=NoAcsDetectionProfileParams(),
            stabilization_delay=0.1,  # Delay to stabilize after moving backward
        )


class RelativeForward(NavigationTask):
    """
    Navigation task to move the robot a specified distance forward.

    Args:
        distance (float): The distance to move forward in millimeters.
    """

    def __init__(self, distance: float):
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
    """
    Navigation task to go to the centroid of a given zone.

    Args:
        zone_id (int): The ID of the target zone.
    """

    def __init__(self, zone_id: int):
        super().__init__(
            goal=zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55, width_view=40
            ),
            stabilization_delay=0.5,
        )

        self.zone_id: int = zone_id

    def _initialize(self, ctx: BaseGameContext) -> None:
        """
        Initialize the task by computing the target position based on the zone's centroid.

        Args:
            ctx (BaseGameContext): The game context providing arena information.
        """
        self._is_initialized = True

        # Compute the goal position with orientation
        go_to_position: OrientedPoint = ctx.arena.compute_goal_position(self.zone_id)
        centroid: Point = ctx.arena.zones[self.zone_id].polygon.centroid
        centroid_with_theta: OrientedPoint = OrientedPoint(
            centroid.x, centroid.y, go_to_position.theta
        )

        # Create a NavigatorTask using the calculated goal
        self.navigator_task: NavigatorTask = NavigatorTask(
            params=NavigatorTaskParams(
                goal=centroid_with_theta,
                timeout=self.timeout,
                path_planner_params=self.path_planner_params,
                trajectory_planner_params=self.trajectory_planner_params,
                speed_profiler=self.speed_profiler,
                avoidance_params=self.avoidance_params,
                acs_detection_profile_params=self.acs_detection_profile_params,
                stabilization_delay=self.stabilization_delay,
            )
        )
