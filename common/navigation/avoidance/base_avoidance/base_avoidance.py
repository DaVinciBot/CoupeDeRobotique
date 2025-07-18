# ====== Code Summary ======
# This module defines the abstract BaseAvoidance class, which serves as a foundational component for
# implementing various obstacle avoidance strategies in a robotic navigation system. It provides utility
# methods for Automatic Collision System (ACS) checks, task state handling, timeout control, and a
# standardized interface for implementing strategy-specific logic via the abstract `handle` method.


from __future__ import annotations

import functools
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING, Generic, TypeVar

from loggerplusplus import Logger

from navigation.avoidance.acs_detection_profiles import (
    AcsDetectionProfileFactory,
    BaseAcsDetectionProfileParams,
)
from navigation.avoidance.base_avoidance.base_avoidance_params import (
    BaseAvoidanceParams,
)
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.trajectory_planner import TrajectoryPlanCommand

if TYPE_CHECKING:
    from arena import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.navigator.task.navigator_task import NavigatorTask

ParamsType = TypeVar("ParamsType", bound=BaseAvoidanceParams)


class BaseAvoidance(ABC, Generic[ParamsType]):
    """Abstract base class providing shared utilities for avoidance strategies.

    This class encapsulates ACS-based obstacle detection, timeout-based abort handling,
    and a standardized interface for strategy-specific logic.
    """

    def __init__(
        self,
        params: ParamsType,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the base avoidance class.

        Args:
            params (ParamsType): Parameters for the avoidance strategy.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for the ACS detection profile.
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        self.logger: Logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: ParamsType = params

        self.acs_detector = AcsDetectionProfileFactory.instantiate(
            params=acs_detection_profile_params,
        )

        self.state: AvoidanceState = AvoidanceState.IDLE
        self._avoiding_start_time: float | None = None  # Timer for avoidance timeout
        self._original_task: NavigatorTask | None = (
            None  # Storage for original navigation task
        )

    def _store_original_task(self, current_navigator_task: NavigatorTask) -> None:
        """Store a deep copy of the original navigation task if not already stored.

        Args:
            current_navigator_task (NavigatorTask): The current navigation task.
        """
        if self._original_task is None and self.state == AvoidanceState.IDLE:
            import copy

            self._original_task = copy.deepcopy(current_navigator_task)

    @staticmethod
    def _ensure_original_task_storage(method: callable) -> callable:
        """Decorator to ensure original task is stored before handling logic is applied.

        Args:
            method (callable): The method to wrap.

        Returns:
            callable: Wrapped method that stores the original task first.
        """

        @functools.wraps(method)
        def wrapper(self, current_navigator_task: NavigatorTask, *args, **kwargs):
            self._store_original_task(current_navigator_task)
            return method(self, current_navigator_task, *args, **kwargs)

        return wrapper

    def _start_timer(self) -> None:
        """Begin the avoidance timeout countdown."""
        self._avoiding_start_time = time.time()

    def _reset_timer(self) -> None:
        """Clear the avoidance timer."""
        self._avoiding_start_time = None

    def _has_timed_out(self) -> bool:
        """Determine whether the avoidance process has timed out.

        Returns:
            bool: `True` if the elapsed time exceeds the timeout threshold.
        """
        if self._avoiding_start_time is None or self.params.timeout is None:
            return False
        return (time.time() - self._avoiding_start_time) > self.params.timeout

    def _abort(
        self,
        task: NavigatorTask,
        position: OrientedPoint,
    ) -> TrajectoryPlanCommand:
        """Abort the avoidance procedure and return a stop command.

        Args:
            task (NavigatorTask): The task being executed.
            position (OrientedPoint): The current position for stopping.

        Returns:
            TrajectoryPlanCommand: A command instructing the system to stop.
        """
        from navigation.navigator.task.states import NavigatorTaskState

        self.state = AvoidanceState.ABORTED
        task.state = NavigatorTaskState.AVOIDING
        cmd = TrajectoryPlanCommand.create_stop_command(current_position=position)
        task.current_trajectory_command = cmd
        self._reset_timer()
        return cmd

    @abstractmethod
    def handle(
        self,
        current_navigator_task: NavigatorTask,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Abstract method for avoidance logic to be implemented by concrete subclasses.

        Args:
            current_navigator_task (NavigatorTask): Current task in progress.
            ally_zone (AllyZone): Ally's current zone data.
            enemy_zone (EnemyZone): Enemy's current zone data.

        Returns:
            TrajectoryPlanCommand: The appropriate trajectory command to execute.
        """
        ...
