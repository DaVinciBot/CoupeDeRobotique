# TODO: to implement !

# ====== Code Summary ======
# ...

# ====== Standard Library Imports ======
import math

# ====== Third-party Library Imports ======
from loggerplusplus import Logger

# ====== Internal Project Imports ======
from geometry import OrientedPoint

# ====== Local Project Imports ======
# Structures
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

# Trajectory planner class & parameters
from navigation.trajectory_planner.basic_trajectory_planner.basic_trajectory_planner_params import \
    BasicTrajectoryPlannerParams
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner

# Speed profile
from navigation.trajectory_planner.speed_profile import SpeedProfiler

# Segments
from navigation.trajectory_planner.sequential_trajectory_planner.segments import (
    BaseSegment, StraightSegment, RotationSegment, StopSegment, SegmentMapper
)


# ====== Sequential Trajectory Planner Class ======
class BasicTrajectoryPlanner(BaseTrajectoryPlanner[BasicTrajectoryPlannerParams]):
    """
    Planner that constructs a sequential series of trajectory segments (rotate, move straight, rotate, stop)
    from a path of oriented points. Supports time-based segment retrieval to provide motion commands.
    """

    def __init__(
            self,
            params: BasicTrajectoryPlannerParams,
            speed_profiler: SpeedProfiler,
            logger: Logger | None = None
    ) -> None:
        super().__init__(params, speed_profiler, logger)

    def plan_trajectory(self, path: list[OrientedPoint]) -> None:
        ...

    @BaseTrajectoryPlanner._ensure_planning_started
    def get_plan(self) -> TrajectoryPlanCommand:
        ...

    def get_total_duration(self) -> float:
        ...
