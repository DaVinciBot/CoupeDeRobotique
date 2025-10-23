"""Abstract base class for trajectory planning components."""

from __future__ import annotations

import functools
import math
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from loggerplusplus import Logger

from geometry import OrientedPoint
from navigation.path_planner import Direction
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner_params import (  # noqa: E501
    BaseTrajectoryPlannerParams,
)
from navigation.trajectory_planner.structs import TrajectoryPlanCommand

if TYPE_CHECKING:
    from collections.abc import Callable

    from navigation.trajectory_planner.segments import (
        RotationSegment,
        StraightSegment,
    )
    from navigation.trajectory_planner.speed_profile import SpeedProfiler


class BaseTrajectoryPlanner[PARAMSTYPE: BaseTrajectoryPlannerParams](ABC):
    """Abstract base class for all trajectory planners.

    Provides lifecycle control (start/stop), time-tracking utilities, and
    logging support. Subclasses must implement specific planning logic and
    expose a method to retrieve the current trajectory command and total
    duration.
    """

    def __init__(
        self,
        params: PARAMSTYPE,
        speed_profiler: SpeedProfiler,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the base trajectory planner.

        Args:
            params (PARAMSTYPE): Planner configuration parameters.
            speed_profiler (SpeedProfiler): Speed profile manager.
            logger (Logger | None, optional):
                Logger instance for debugging. Defaults to ``None``.
        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: PARAMSTYPE = params
        self.speed_profiler: SpeedProfiler = speed_profiler
        self._is_backward: bool = self.params.direction == Direction.BACKWARD

        # Attributes dedicated to the trajectory planning process
        self._start_trajectory_elapsed_time_checkpoint: float = (
            0.0  # Accumulated time from previous sessions
        )
        self._start_trajectory_timestamp: float = (
            0.0  # Time when current planning started
        )

    # region ====== Chrono Helpers ======
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

    def get_trajectory_time_elapsed(self) -> float:
        """Return the elapsed planning time.

        Returns:
            float: Elapsed time in seconds.
        """
        return self._get_trajectory_time_elapsed()

    # endregion

    # region ====== Internal Utilities ======
    @staticmethod
    def ensure_planning_started(
        method: Callable[..., TrajectoryPlanCommand],
    ) -> Callable[..., TrajectoryPlanCommand]:
        """Decorator to ensure that planning has started before executing a method.

        Args:
            method (Callable[..., TrajectoryPlanCommand]): The method to wrap.

        Returns:
            Callable[..., TrajectoryPlanCommand]: Wrapped method.
        """

        @functools.wraps(method)
        def wrapper(self: BaseTrajectoryPlanner[PARAMSTYPE]) -> TrajectoryPlanCommand:
            # Start planning if not already started
            if not self.is_planning_started():
                self.start_planning()

            # Execute the method
            return method(self)

        return wrapper

    def _get_rotation_command(
        self,
        segment: RotationSegment,
        local_time: float | None,
    ) -> TrajectoryPlanCommand:
        """Get trajectory command for a rotation segment.

        Args:
            segment (RotationSegment): The rotation segment.
            local_time (float | None): Time elapsed within this segment.

        Returns:
            TrajectoryPlanCommand: Command for rotation.

        Raises:
            ValueError: If segment start position theta is None.
        """
        if segment.start_position.theta is None:
            msg = "Segment start position theta must be defined for rotation."
            raise ValueError(msg)

        rotation = self.speed_profiler.angular_speed_profile.get_distance(
            time_elapsed=local_time,
            distance=segment.rotation,
        )

        theta = segment.start_position.theta + rotation * segment.sign

        return TrajectoryPlanCommand(
            position=OrientedPoint(
                segment.start_position.x,
                segment.start_position.y,
                theta,
            ),
            linear_speed=0.0,
            angular_speed=self.speed_profiler.angular_speed_profile.get_speed(
                time_elapsed=local_time,
                distance=segment.rotation,
            ),
        )

    def _get_straight_command(
        self,
        segment: StraightSegment,
        local_time: float | None,
    ) -> TrajectoryPlanCommand:
        """Get trajectory command for a straight segment.

        Args:
            segment (StraightSegment): The straight segment.
            local_time (float | None): Time elapsed within this segment.

        Returns:
            TrajectoryPlanCommand: Command for straight motion.

        Raises:
            ValueError: If segment start position theta is None.
        """
        if segment.start_position.theta is None:
            msg = "Segment start position theta must be defined for straight."
            raise ValueError(msg)

        traveled_distance = self.speed_profiler.linear_speed_profile.get_distance(
            time_elapsed=local_time,
            distance=abs(segment.distance),
        )

        if self._is_backward:
            x = segment.start_position.x - traveled_distance * math.cos(
                segment.start_position.theta,
            )
            y = segment.start_position.y - traveled_distance * math.sin(
                segment.start_position.theta,
            )
        else:
            x = segment.start_position.x + traveled_distance * math.cos(
                segment.start_position.theta,
            )
            y = segment.start_position.y + traveled_distance * math.sin(
                segment.start_position.theta,
            )

        return TrajectoryPlanCommand(
            position=OrientedPoint(x, y, segment.start_position.theta),
            linear_speed=self.speed_profiler.linear_speed_profile.get_speed(
                time_elapsed=local_time,
                distance=abs(segment.distance),
            ),
            angular_speed=0.0,
        )

    # endregion

    # region ====== Public Methods ======
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
            bool: ``True`` if planning is active, ``False`` otherwise.
        """
        return self._start_trajectory_timestamp > 0.0

    # endregion

    # region ====== Abstract Methods ======
    @abstractmethod
    def plan_trajectory(self, path: list[OrientedPoint]) -> None:
        """Plan a trajectory for the provided path.

        Args:
            path (list[OrientedPoint]): The path to follow.
        """

    @abstractmethod
    def get_plan(self) -> TrajectoryPlanCommand:
        """Return the current trajectory command.

        Returns:
            TrajectoryPlanCommand: The current trajectory command.
        """

    @abstractmethod
    def get_total_duration(self) -> float:
        """Return the total duration of the planned trajectory.

        Returns:
            float: Total duration in seconds.
        """

    # endregion
