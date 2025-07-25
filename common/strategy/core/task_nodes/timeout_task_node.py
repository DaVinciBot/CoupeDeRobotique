from __future__ import annotations

import time
from typing import TYPE_CHECKING

from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.tasks import BaseTask, TaskStatus

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.task_nodes.scoring_functions import (
        BaseScoringFunction,
    )


class TimeoutTaskNode(BaseTaskNode):
    """A task node with a hard timeout: if tasks do not complete within the given duration,
    the node triggers a timeout and stops execution.
    """

    def __init__(
        self,
        name: str,
        tasks: BaseTask | list[BaseTask],
        timeout_seconds: float,
        scoring_function: BaseScoringFunction | None = None,
    ) -> None:
        """Initialize the timeout node.

        Args:
            name (str): Node name.
            tasks (BaseTask | list[BaseTask]): Task or tasks to execute.
            timeout_seconds (float): Duration in seconds before timeout occurs.
            scoring_function (BaseScoringFunction | None, optional): Scoring strategy used when evaluating transitions. Defaults to None.
        """
        super().__init__(name, tasks, scoring_function)
        self.timeout_seconds: float = timeout_seconds
        self._timeout_triggered: bool = False
        self.logger.info(
            f"Initialized TimeoutTaskNode '{self.name}' with timeout set to {self.timeout_seconds}s",
        )

    def on_timeout(self, ctx: BaseGameContext) -> None:
        """Hook called once when the timeout is reached.

        Args:
            ctx (BaseGameContext): Current game context.

        This method can be overridden in subclasses to implement custom
        behaviour when the timeout triggers.
        """
        self.logger.warning(
            f"Timeout reached for node '{self.name}' after {self.timeout_seconds:.2f}s",
        )

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
            self.logger.debug(
                f"TimeoutTaskNode '{self.name}' already completed with status {self.status.name}",
            )
            return True

        now = time.time()

        # On first run, start timer and status
        if self.start_time is None:
            self.start_time = now
            self.status = TaskStatus.IN_PROGRESS
            self.logger.info(
                f"Started TimeoutTaskNode '{self.name}'; will timeout after {self.timeout_seconds:.2f}s",
            )

        elapsed = now - self.start_time
        self.logger.debug(
            f"Node '{self.name}' elapsed time: {elapsed:.2f}s of {self.timeout_seconds:.2f}s",
        )

        # Check for timeout
        if elapsed >= self.timeout_seconds:
            if not self._timeout_triggered:
                self.on_timeout(ctx)
                self._timeout_triggered = True
            self.status = TaskStatus.TIMEOUT
            self.end_time = now
            self.logger.info(f"TimeoutTaskNode '{self.name}' status set to TIMEOUT")
            return True

        # Delegate to base execution if within timeout
        return super().execute(ctx)
