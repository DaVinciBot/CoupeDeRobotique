from navigation.path_planner import BasePathPlannerParams
from navigation.trajectory_planner import BaseTrajectoryPlannerParams
from navigation.trajectory_planner.speed_profile import SpeedProfiler

from navigation.avoidance.base_avoidance import BaseAvoidanceParams
from navigation.avoidance.acs_detection_profiles import BaseAcsDetectionProfileParams

from geometry import OrientedPoint


class NavigatorTaskParams:
    def __init__(
        self,
        # Attributes
        goal: OrientedPoint | None,
        timeout: float | None,
        stabilization_delay: float,
        # Parameters
        path_planner_params: BasePathPlannerParams,
        trajectory_planner_params: BaseTrajectoryPlannerParams,
        speed_profiler: SpeedProfiler,
        avoidance_params: BaseAvoidanceParams,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
    ):
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
        self.timeout: float = timeout
        self.stabilization_delay: float = stabilization_delay
