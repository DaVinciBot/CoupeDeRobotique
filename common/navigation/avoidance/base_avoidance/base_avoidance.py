"""Abstract base class for obstacle avoidance strategies."""

from __future__ import annotations

import copy
import functools
import time
from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from log_manager import LogLogger
from navigation.avoidance.acs_detection_profiles import AcsDetectionProfileFactory
from navigation.avoidance.base_avoidance.base_avoidance_params import (
    BaseAvoidanceParams,
)
from navigation.avoidance.base_avoidance.states import AvoidanceState
from navigation.navigator.task.states import NavigatorTaskState
from navigation.trajectory_planner import TrajectoryPlanCommand

if TYPE_CHECKING:
    from collections.abc import Callable

    from loggerplusplus import Logger

    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from geometry import OrientedPoint
    from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
        BaseAcsDetectionProfileParams,
    )
    from navigation.navigator.task.navigator_task import NavigatorTask


class BaseAvoidance[PARAMSTYPE: BaseAvoidanceParams](ABC):
    """Abstract base class providing shared utilities for avoidance strategies.

    This class encapsulates ACS-based obstacle detection, timeout-based abort
    handling, and a standardized interface for strategy-specific logic.
    """

    def __init__(
        self,
        params: PARAMSTYPE,
        acs_detection_profile_params: BaseAcsDetectionProfileParams,
        logger: Logger | None = None,
    ) -> None:
        """Initialize the base avoidance class.

        Args:
            params (PARAMSTYPE): Parameters for the avoidance strategy.
            acs_detection_profile_params (BaseAcsDetectionProfileParams):
                Parameters for the ACS detection profile.
            logger (Logger | None, optional): Logger instance for debugging.
                Defaults to ``None``.
        """
        self._logger: Logger = logger or LogLogger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.params: PARAMSTYPE = params

        self.acs_detector = AcsDetectionProfileFactory.instantiate(
            params=acs_detection_profile_params,
        )

        self.state: AvoidanceState = AvoidanceState.IDLE
        self._avoiding_start_time: float | None = None  # Timeout timer
        self._original_task: NavigatorTask | None = None
        # Storage for original navigation task

    def _store_original_task(
        self,
        current_navigator_task: NavigatorTask,
    ) -> None:
        """Store a deep copy of the original navigation task if not already stored.

        Args:
            current_navigator_task (NavigatorTask): The current navigation task.
        """
        if self._original_task is None and self.state == AvoidanceState.IDLE:
            self._original_task = copy.deepcopy(current_navigator_task)

    @staticmethod
    def ensure_original_task_storage(
        method: Callable[..., TrajectoryPlanCommand],
    ) -> Callable[..., TrajectoryPlanCommand]:
        """Decorator to ensure original task is stored before handling logic is applied.

        Args:
            method (Callable[..., TrajectoryPlanCommand]): The method to wrap.

        Returns:
            Callable[..., TrajectoryPlanCommand]:
                Wrapped method that stores the original task first.
        """

        @functools.wraps(method)
        def wrapper(
            self: BaseAvoidance[PARAMSTYPE],
            current_navigator_task: NavigatorTask,
            ally_zone: AllyZone,
            enemy_zone: EnemyZone,
        ) -> TrajectoryPlanCommand:
            self._store_original_task(current_navigator_task)
            return method(self, current_navigator_task, ally_zone, enemy_zone)

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
            bool: ``True`` if the elapsed time exceeds the timeout threshold.
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
