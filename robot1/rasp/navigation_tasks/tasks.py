from config_loader import CONFIG
from navigation import (
    BasicPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    LinearRampedSpeedProfile,
    SpeedProfiler,
    StopAndWaitAvoidanceParams,
    NavigatorTaskParams,
)
from geometry import OrientedPoint


yellow_start_tasks = [
    # Point 1
    NavigatorTaskParams(
        goal=OrientedPoint(110, 90, 0),
        timeout=None,
        path_planner_params=BasicPathPlannerParams(),
        trajectory_planner_params=SequentialTrajectoryPlannerParams(),
        speed_profiler=SpeedProfiler(
            linear_speed_profile=LinearRampedSpeedProfile(
                acceleration=10.0, max_speed=20.0, deceleration=5.0
            ),
            angular_speed_profile=LinearRampedSpeedProfile(
                acceleration=1.0, max_speed=2.0, deceleration=0.5
            ),
        ),
        avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
        acs_detection_profile_params=CONFIG.ACS_PROFILE_START_TASK,
    ),
    # Point 2
    NavigatorTaskParams(
        goal=OrientedPoint(75, 87.5, 0),
        timeout=None,
        path_planner_params=BasicPathPlannerParams(),
        trajectory_planner_params=SequentialTrajectoryPlannerParams(),
        speed_profiler=SpeedProfiler(
            linear_speed_profile=LinearRampedSpeedProfile(
                acceleration=10.0, max_speed=20.0, deceleration=5.0
            ),
            angular_speed_profile=LinearRampedSpeedProfile(
                acceleration=1.0, max_speed=2.0, deceleration=0.5
            ),
        ),
        avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
        acs_detection_profile_params=CONFIG.ACS_PROFILE_START_TASK,
    ),
    # Point 3
    NavigatorTaskParams(
        goal=OrientedPoint(83, 165, 0),
        timeout=None,
        path_planner_params=BasicPathPlannerParams(),
        trajectory_planner_params=SequentialTrajectoryPlannerParams(),
        speed_profiler=SpeedProfiler(
            linear_speed_profile=LinearRampedSpeedProfile(
                acceleration=10.0, max_speed=20.0, deceleration=5.0
            ),
            angular_speed_profile=LinearRampedSpeedProfile(
                acceleration=1.0, max_speed=2.0, deceleration=0.5
            ),
        ),
        avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
        acs_detection_profile_params=CONFIG.ACS_PROFILE_START_TASK,
    ),
    # Point 4
    NavigatorTaskParams(
        goal=OrientedPoint(22, 50, 0),
        timeout=None,
        path_planner_params=BasicPathPlannerParams(),
        trajectory_planner_params=SequentialTrajectoryPlannerParams(),
        speed_profiler=SpeedProfiler(
            linear_speed_profile=LinearRampedSpeedProfile(
                acceleration=10.0, max_speed=20.0, deceleration=5.0
            ),
            angular_speed_profile=LinearRampedSpeedProfile(
                acceleration=1.0, max_speed=2.0, deceleration=0.5
            ),
        ),
        avoidance_params=StopAndWaitAvoidanceParams(timeout=10),
        acs_detection_profile_params=CONFIG.ACS_PROFILE_START_TASK,
    ),
]
