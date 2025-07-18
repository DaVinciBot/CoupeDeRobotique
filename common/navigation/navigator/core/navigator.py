from collections import deque

from loggerplusplus import Logger

from arena import AllyZone, EnemyZone
from navigation.avoidance import AvoidanceState
from navigation.navigator.signals import (
    NavigatorSignalsDispatcher,
)
from navigation.navigator.task import (
    NavigatorTask,
    NavigatorTaskParams,
    NavigatorTaskState,
)
from navigation.trajectory_planner import TrajectoryPlanCommand


class Navigator:
    """Navigator class."""

    def __init__(self, logger: Logger | None = None) -> None:
        """Initialize the Navigator.

        Args:
            logger (Logger | None, optional): Logger instance for debugging. Defaults to None.
        """
        self.logger = logger or Logger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self._events_manager: NavigatorSignalsDispatcher = NavigatorSignalsDispatcher()

        # Only for task params (instantiate the task when needed)
        self._tasks_queue: deque[NavigatorTaskParams] = deque()
        self.current_task: NavigatorTask | None = None

    def _fetch_next_task(self) -> bool:
        """Fetch the next task from the queue.

        Returns:
            bool: `True` if a new task was fetched, `False` if the queue is empty.
        """
        if self._tasks_queue:
            self.current_task: NavigatorTask = NavigatorTask(
                params=self._tasks_queue.popleft(),
            )
            self.logger.info(f"Switched to new task: {self.current_task}")
            return True
        self.current_task = None
        return False

    def add_navigation_task(
        self,
        navigator_task_params: NavigatorTaskParams,
        skip_queue: bool = False,
    ) -> None:
        """Add a navigation task to the queue.

        Args:
            navigator_task_params (NavigatorTaskParams): The parameters for the navigation task.
            skip_queue (bool, optional): If `True`, skip the queue and execute the task immediately. Defaults to `False`.
        """
        if skip_queue:
            self.abort(affect_all_tasks=False)
            self._fetch_next_task()
            self.logger.info(f"Executing task immediately: {navigator_task_params}")
        else:
            self._tasks_queue.append(navigator_task_params)
            self.logger.info(f"Added task to queue: {navigator_task_params}")

        if self.current_task is None:
            self._fetch_next_task()
            self.logger.info(f"Executing task: {self.current_task}")

    def handle(
        self,
        ally_zone: AllyZone,
        enemy_zone: EnemyZone,
    ) -> TrajectoryPlanCommand:
        """Handle the navigation task.

        Args:
            ally_zone (AllyZone): The ally zone.
            enemy_zone (EnemyZone): The enemy zone.

        Returns:
            TrajectoryPlanCommand: The trajectory plan command.
        """
        # besoins: ally_position_zone, enemy_position_zone, grid, dynamic_grid (comment déclancher sa mis à jour que quand l'ennemi est proche)

        # No current task -> do nothing (current task can't be none if there are tasks in the queue)
        if self.current_task is None:
            return TrajectoryPlanCommand.create_stop_command(
                current_position=ally_zone.point,
            )

        task_cmd: TrajectoryPlanCommand = self.current_task.handle(
            ally_zone,
            enemy_zone,
        )

        # If avoidance is active => check avoidance state and return avoidance command
        if (
            self.current_task.state == NavigatorTaskState.AVOIDING
            and self.current_task.avoidance.state == AvoidanceState.ABORTED
        ):
            self.abort()
            self._fetch_next_task()
            self.logger.info("Avoidance aborted.")

        # If task is finished => fetch next task
        if self.current_task.state == NavigatorTaskState.FINISHED:
            self._fetch_next_task()
            self.logger.info("Task finished.")

        return task_cmd

    def abort(self, affect_all_tasks: bool = False) -> None:
        """Abort the current task and all tasks in the queue.

        Args:
            affect_all_tasks (bool, optional): If `True`, all tasks in the queue will be aborted. Defaults to `False`.
        """
        if affect_all_tasks:
            self._tasks_queue.clear()
            self.logger.info("All tasks aborted.")

        self.current_task = None
        self.logger.info("Current task aborted.")
