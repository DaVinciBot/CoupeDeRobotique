"""Navigation task directing the robot to a stuff zone for pickup."""

from a_config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask
from navigation import (
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    StopAndWaitAvoidanceParams,
)
from navigation.avoidance.acs_detection_profiles.rectangular_projection_acs_detection_profile import (
    RectangularProjectionAcsDetectionProfileParams,
)


class GoToStuffZoneToPickUp(NavigationTask):
    """Navigation task to move the robot to a specified 'stuff zone' for a pickup operation.

    This class configures the required navigation parameters such as path planning, trajectory planning,
    speed profiling, and avoidance strategies. It utilizes a rectangular projection ACS detection profile
    to avoid collisions and applies a stabilization delay for system readiness before performing tasks.

    """

    def __init__(self, stuff_zone_id: int) -> None:
        """Initialize the GoToStuffZoneToPickUp task with parameters for navigation and avoidance.

        Args:
            stuff_zone_id (int): Identifier for the target stuff zone location.

        """
        super().__init__(
            goal=stuff_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                step_sleep_delay=2,
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,  # Use for pickup speed profiler
            avoidance_params=StopAndWaitAvoidanceParams(timeout=20),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=2,
        )
