"""Navigation task to reach a color-reserved zone."""

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


class GoToColorReservedZoneToFinishGame(NavigationTask):
    """Task to navigate to a color reserved zone to finish the game."""

    def __init__(self, color_reserved_zone_id: int) -> None:
        """Initialize the GoToColorReservedZoneToFinishGame task.

        Args:
            color_reserved_zone_id (int): The ID of the target color reserved zone.

        """
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=50,
                width_view=40,
            ),
            stabilization_delay=0.5,
        )


class GoToColorReservedZoneToConstruct(NavigationTask):
    """Task to navigate to a color reserved zone to construct."""

    def __init__(self, color_reserved_zone_id: int) -> None:
        """Initialize the GoToColorReservedZoneToConstruct task.

        Args:
            color_reserved_zone_id (int): The ID of the target color reserved zone.

        """
        super().__init__(
            goal=color_reserved_zone_id,
            path_planner_params=BasicPathPlannerParams(),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=55,
                width_view=40,
            ),
            stabilization_delay=1,  # Delay to stabilize before construction
        )
