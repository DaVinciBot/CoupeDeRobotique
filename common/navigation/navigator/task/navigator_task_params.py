"""Parameter container for a navigation task."""

from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from geometry import OrientedPoint
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

DEFAULT_ANGLE_REACHED_TOLERANCE_RAD = 0.05
DEFAULT_POSITION_REACHED_TOLERANCE_CM = 1.0


class NavigatorTaskParams:
    """Parameters for a navigation task."""

    def __init__(
        self,
        # Attributes
        goal: OrientedPoint | None,
        timeout: float | None,
        stabilization_delay: float,
        position_reached_tolerance_cm: float,
        angle_reached_tolerance_rad: float,
        finish_after_expected_end_delay_s: float | None,
        # Parameters
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
    ) -> None:
        """Initialize the NavigatorTaskParams.

        Args:
            goal (OrientedPoint | None): The goal to reach.
            timeout (float | None): The timeout for the task.
            stabilization_delay (float): The stabilization delay.
            position_reached_tolerance_cm (float):
                Accepted position error before considering the goal reached.
            angle_reached_tolerance_rad (float):
                Accepted orientation error before considering the goal reached.
            finish_after_expected_end_delay_s (float | None):
                Extra time after the planned trajectory duration before considering
                the task finished even if the goal is not reached.
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

        self.goal: OrientedPoint | None = goal
        self.timeout: float | None = timeout
        self.stabilization_delay: float = stabilization_delay
        self.position_reached_tolerance_cm: float = position_reached_tolerance_cm
        self.angle_reached_tolerance_rad: float = angle_reached_tolerance_rad
        self.finish_after_expected_end_delay_s: float | None = (
            finish_after_expected_end_delay_s
        )
