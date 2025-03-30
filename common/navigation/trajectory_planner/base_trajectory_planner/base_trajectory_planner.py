# ====== Code Summary ======
# This module defines an abstract base class `BaseTrajectoryPlanner` designed to manage trajectory planning
# in navigation systems. It provides lifecycle control (start/stop), time tracking utilities, and enforces
# implementation of a planning method in subclasses. The class is generic and supports parameterization and logging.

# ====== Standard Library Imports ======
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import functools
import time

# ====== Third-Party Imports ======
from loggerplusplus import Logger

# ====== Internal Project Imports ======
from geometry import OrientedPoint

# ====== Local Imports ======
from navigation.trajectory_planner.structs import TrajectoryPlanCommand
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.speed_profile import SpeedProfiler

# ====== Type Hint ======
ParamsType = TypeVar("ParamsType", bound=BaseTrajectoryPlannerParams)


# ====== Base Trajectory Planner Class ======
class BaseTrajectoryPlanner(ABC, Generic[ParamsType]):
    def __init__(self, params: ParamsType, speed_profiler: SpeedProfiler, logger: Logger | None = None) -> None:
        if logger is None:
            logger = Logger(identifier=self.__class__.__name__, follow_logger_manager_rules=True)

        self.logger: Logger = logger
        self.params: ParamsType = params
        self.speed_profiler: SpeedProfiler = speed_profiler

        # Attributes dedicated to the trajectory planning process
        self._start_trajectory_elapsed_time_checkpoint: float = 0.0  # Accumulated time from previous sessions
        self._start_trajectory_timestamp: float = 0.0  # Time when current planning started

    # ====== Chrono Helpers ======
    def _get_trajectory_time_elapsed(self) -> float:
        if not self.is_planning_started():  # If planning has not started, return 0.0
            return 0.0

        return (
                time.time() - self._start_trajectory_timestamp
                + self._start_trajectory_elapsed_time_checkpoint
        )

    # ====== Internal Utilities ======
    def _ensure_planning_started(self, method: callable) -> callable:

        @functools.wraps(method)
        def wrapper(*args, **kwargs):
            # Start planning if not already started
            if not self.is_planning_started():
                self.start_planning()

            # Execute the method
            return method(*args, **kwargs)

        return wrapper

    # ====== Public Methods ======
    def start_planning(self) -> None:

        self._start_trajectory_timestamp = time.time()

    def stop_planning(self) -> None:

        self._start_trajectory_elapsed_time_checkpoint += (
                time.time() - self._start_trajectory_timestamp
        )

    def is_planning_started(self) -> bool:

        return self._start_trajectory_timestamp > 0.0

    # ====== Abstract Methods ======
    @abstractmethod
    def plan_trajectory(self, path: list[OrientedPoint], **kwargs) -> None:
        ...

    @abstractmethod
    def get_plan(self, **kwargs) -> TrajectoryPlanCommand:
        ...
