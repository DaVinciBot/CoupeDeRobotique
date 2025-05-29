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


class GoToStuffZoneToPickUp(NavigationTask):
    def __init__(self, stuff_zone_id: int):
        super().__init__(
            goal=stuff_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_TO_PICKUP_SPEED_PROFILER,  # Use for pickup speed profiler
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50, width_view=40
            ),
        )
