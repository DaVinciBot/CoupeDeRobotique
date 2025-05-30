# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation import (
    StopAndWaitAvoidanceParams,
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)


class GoToColorReservedZoneToFinishGame(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50, width_view=40
            ),
            stabilization_delay=0.5,
        )


class GoToColorReservedZoneToConstruct(NavigationTask):
    def __init__(self, color_reserved_zone_id: int):
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55, width_view=40
            ),
            stabilization_delay=1,  # Delay to stabilize before construction
        )
