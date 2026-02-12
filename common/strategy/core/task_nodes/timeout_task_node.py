"""Task node enforcing a maximum execution time for its tasks."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Any, override

from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.tasks import BaseTask, TaskStatus

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.scoring_functions import BaseScoringFunction


class TimeoutTaskNode(BaseTaskNode):
    """A task node that stops execution after a fixed duration."""

    def __init__(
        self,
        name: str,
        tasks: BaseTask[Any] | list[BaseTask[Any]],
        timeout_seconds: float,
        scoring_function: BaseScoringFunction | None = None,
    ) -> None:
        """Initialize the timeout node.

        Args:
            name (str): Node name.
            tasks (BaseTask[Any] | list[BaseTask[Any]]): Task or tasks to execute.
            timeout_seconds (float): Duration in seconds before timeout occurs.
            scoring_function (BaseScoringFunction | None, optional):
                Scoring strategy used when evaluating transitions. Defaults to None.
        """
        super().__init__(name, tasks, scoring_function)
        self.timeout_seconds: float = timeout_seconds
        self._timeout_triggered: bool = False
        self.status = TaskStatus.PENDING
        self.start_time = None
        self.end_time: float | None = None
        self._logger.info(
            "[STRAT] Initialized TimeoutTaskNode: "
            f"'{self.name}' (timeout: {self.timeout_seconds}s)",
        )

    def on_timeout(self, _ctx: BaseGameContext) -> None:
        """Hook called once when the timeout is reached.

        Args:
            _ctx (BaseGameContext): Current game context.

        This method can be overridden in subclasses to implement custom
        behaviour when the timeout triggers.
        """
        self._logger.warning(
            f"[STRAT] Timeout reached: '{self.name}' ({self.timeout_seconds:.2f}s)",
        )

    @override
    def execute(self, ctx: BaseGameContext) -> bool:
        """Execute tasks but enforce a maximum duration.

        Args:
            ctx (BaseGameContext): Game context used for task execution.

        Returns:
            bool: ``True`` if all tasks completed or a timeout occurred,
            ``False`` otherwise.
        """
        # If already completed, no-op
        if self.status in {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.TIMEOUT}:
            self._logger.debug(
                f"[STRAT] TimeoutTaskNode '{self.name}' "
                f"already completed: {self.status.name}",
            )
            return True

        now = time.time()

        # On first run, start timer and status
        if self.start_time is None:
            self.start_time = now
            self.status = TaskStatus.IN_PROGRESS
            self._logger.info(
                f"[STRAT] Started TimeoutTaskNode: '{self.name}' "
                f"(timeout: {self.timeout_seconds:.2f}s)",
            )

        elapsed = now - self.start_time
        self._logger.debug(
            f"[STRAT] Node '{self.name}' "
            f"elapsed: {elapsed:.2f}s / {self.timeout_seconds:.2f}s",
        )

        # Check for timeout
        if elapsed >= self.timeout_seconds:
            if not self._timeout_triggered:
                self.on_timeout(ctx)
                self._timeout_triggered = True
            self.status = TaskStatus.TIMEOUT
            self.end_time = now
            self._logger.info(
                f"[STRAT] TimeoutTaskNode '{self.name}' status: TIMEOUT",
            )
            return True

        # Delegate to base execution if within timeout
        return super().execute(ctx)
