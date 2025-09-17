"""Parameter container for a navigation task."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry import OrientedPoint, Point
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
        BaseAcsDetectionProfileParams,
    )
    from navigation.avoidance.base_avoidance.base_avoidance_params import (
        BaseAvoidanceParams,
    )
    from navigation.path_planner.base_path_planner import BasePathPlannerParams
    from navigation.trajectory_planner.base_trajectory_planner import (
        BaseTrajectoryPlannerParams,
    )
    from navigation.trajectory_planner.speed_profile import SpeedProfiler


class NavigatorTaskParams:
    """Parameters for a navigation task."""

    def __init__(
        self,
        # Attributes
        goal: OrientedPoint | Point | None,
        timeout: float | None,
        stabilization_delay: float,
        # Parameters
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
    ) -> None:
        """Initialize the NavigatorTaskParams.

        Args:
            goal (OrientedPoint | Point | None): The goal to reach.
            timeout (float | None): The timeout for the task.
            stabilization_delay (float): The stabilization delay.
            path_planner_params (BasePathPlannerParams):
                The parameters for the path planner.
            trajectory_planner_params (BaseTrajectoryPlannerParams):
                The parameters for the trajectory planner.
            speed_profiler (SpeedProfiler): The speed profiler.
            avoidance_params (BaseAvoidanceParams): The parameters for the avoidance.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                The parameters for the ACS detection profile.
        """
        self.path_planner_params: BasePathPlannerParams = path_planner_params
        self.trajectory_planner_params: BaseTrajectoryPlannerParams = (
            trajectory_planner_params
        )
        self.speed_profiler: SpeedProfiler = speed_profiler
        self.avoidance_params: BaseAvoidanceParams = avoidance_params
        self.acs_detection_profile_params: BaseAcsDetectionProfileParams = (
            acs_detection_profile_params
        )

        self.goal: OrientedPoint | Point | None = goal
        self.timeout: float | None = timeout
        self.stabilization_delay: float = stabilization_delay
