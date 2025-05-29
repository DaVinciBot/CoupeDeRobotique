from config_loader import CONFIG

from navigation import (
    NoAvoidanceParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    Direction,
    StopAndWaitAvoidanceParams,
)

from navigation.avoidance.acs_detection_profiles import (
    RectangularProjectionAcsDetectionProfileParams,
)

from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask


class GoStraight(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.FORWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=40, width_view=40
            ),
        )


class Rotate(NavigationTask):
    def __init__(self, theta: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(rotation=theta),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.FORWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=40, width_view=40
            ),
        )
