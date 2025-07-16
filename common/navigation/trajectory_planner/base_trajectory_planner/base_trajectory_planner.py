# ====== Code Summary ======
# This module defines an abstract base class `BaseTrajectoryPlanner` designed to manage trajectory planning
# in navigation systems. It provides lifecycle control (start/stop), time tracking utilities, and enforces
# implementation of a planning method in subclasses. The class is generic and supports parameterization and logging.

import functools
import time
from abc import ABC, abstractmethod
from typing import Generic, TypeVar

from loggerplusplus import Logger

from geometry import OrientedPoint
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.speed_profile import SpeedProfiler
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

ParamsType = TypeVar("ParamsType", bound=BaseTrajectoryPlannerParams)


class BaseTrajectoryPlanner(ABC, Generic[ParamsType]):
    """Abstract base class for all trajectory planners.

    Provides lifecycle control (start/stop), time-tracking utilities, and logging support.
    Subclasses must implement specific planning logic and expose a method to retrieve
    the current trajectory command and total duration.
    """

    def __init__(
        self,
        params: ParamsType,
        speed_profiler: SpeedProfiler,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the base trajectory planner.

        Args:
            params (ParamsType): Planner configuration parameters.
            speed_profiler (SpeedProfiler): Speed profile manager.
            logger (Logger | None): Optional logger instance.
        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: ParamsType = params
        self.speed_profiler: SpeedProfiler = speed_profiler

        # Attributes dedicated to the trajectory planning process
        self._start_trajectory_elapsed_time_checkpoint: float = (
            0.0  # Accumulated time from previous sessions
        )
        self._start_trajectory_timestamp: float = (
            0.0  # Time when current planning started
        )

    # ====== Chrono Helpers ======
    def _get_trajectory_time_elapsed(self) -> float:
        """Compute the total elapsed time since the start of the planning session.

        Returns:
            float: Elapsed time in seconds.
        """
        if not self.is_planning_started():  # If planning has not started, return 0.0
            return 0.0

        return (
            time.time()
            - self._start_trajectory_timestamp
            + self._start_trajectory_elapsed_time_checkpoint
        )

    # ====== Internal Utilities ======
    @staticmethod
    def _ensure_planning_started(method: callable) -> callable:
        """Decorator to ensure that planning has started before executing a method.

        Args:
            method (callable): The method to wrap.

        Returns:
            callable: Wrapped method.
        """

        @functools.wraps(method)
        def wrapper(self, *args, **kwargs):
            # Start planning if not already started
            if not self.is_planning_started():
                self.start_planning()

            # Execute the method
            return method(self, *args, **kwargs)

        return wrapper

    # ====== Public Methods ======
    def start_planning(self) -> None:
        """Start the trajectory planning session."""
        self._start_trajectory_timestamp = time.time()

    def stop_planning(self) -> None:
        """Stop the planning session and accumulate elapsed time."""
        self._start_trajectory_elapsed_time_checkpoint += (
            time.time() - self._start_trajectory_timestamp
        )

    def is_planning_started(self) -> bool:
        """Check if planning has been started.

        Returns:
            bool: True if planning is active, False otherwise.
        """
        return self._start_trajectory_timestamp > 0.0

    # ====== Abstract Methods ======
    @abstractmethod
    def plan_trajectory(self, path: list[OrientedPoint]) -> None: ...

    @abstractmethod
    def get_plan(self) -> TrajectoryPlanCommand: ...

    @abstractmethod
    def get_total_duration(self) -> float: ...
