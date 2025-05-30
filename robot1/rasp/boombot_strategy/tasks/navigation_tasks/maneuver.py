# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation import (
    DeltaPathPlannerParams,
    NoAvoidanceParams,
    SequentialTrajectoryPlannerParams,
    Direction,
    BasicPathPlannerParams,
)
from navigation.avoidance.acs_detection_profiles.no_acs_detection_profile import (
    NoAcsDetectionProfileParams,
)

from navigation import (
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)

from strategy.core import BaseGameContext

from navigation import (
    NavigatorTaskParams,
    NavigatorTask,
)

from geometry import OrientedPoint, Point


class RelativeBackward(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=-distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.BACKWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=NoAcsDetectionProfileParams(),
            stabilization_delay=1,  # Delay to stabilize after moving backward
        )


class RelativeForward(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_SLOW_SPEED_PROFILER,
            avoidance_params=NoAvoidanceParams(),
            acs_detection_profile_params=NoAcsDetectionProfileParams(),
            stabilization_delay=1,  # Delay to stabilize after moving forward
        )


class GoCentroidOfZone(NavigationTask):
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
            stabilization_delay=5,
        )

        self.zone_id: int = zone_id

    def _initialize(self, ctx: BaseGameContext) -> None:
        self._is_initialized = True

        go_to_position: OrientedPoint = ctx.arena.compute_goal_position(self.zone_id)
        centroid: Point = ctx.arena.zones[self.zone_id].polygon.centroid
        centroid_with_theta: OrientedPoint = OrientedPoint(
            centroid.x, centroid.y, go_to_position.theta
        )

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
