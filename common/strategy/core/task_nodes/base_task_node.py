# type: ignore[reportImportCycles] TYPE_CHECKING block => no import cycles at runtime
"""Execution unit that runs tasks and handles transitions."""

from __future__ import annotations

import time
import traceback
from typing import TYPE_CHECKING, Any

from loggerplusplus import Logger

from strategy.core.task_nodes.scoring_functions import (
    BaseScoringFunction,
    DefaultScoringFunction,
)
from strategy.core.tasks import BaseTask, TaskStatus

if TYPE_CHECKING:
    from collections.abc import Callable

    from strategy.core.base_game_context import BaseGameContext
    from strategy.core.transitions import BaseTransition


class BaseTaskNode:
    """A node that manages one or more tasks with transitions and scoring."""

    def __init__(
        self,
        name: str,
        tasks: BaseTask | list[BaseTask],
        scoring_function: BaseScoringFunction | None = None,
        points: int | Callable[[BaseGameContext], int] | None = None,
        estimated_duration: float | Callable[[BaseGameContext], float] | None = None,
    ) -> None:
        """Initialize the task node.

        Args:
            name (str): The node name.
            tasks (BaseTask | list[BaseTask]): Single task or list of tasks to execute.
            scoring_function (BaseScoringFunction | None, optional):
                Scoring function used when evaluating transitions. Defaults to None.
            points (int | Callable[[BaseGameContext], int] | None): Points awarded for
                completing this task node, defaults to None.
            estimated_duration (float | Callable[[BaseGameContext], float] | None):
                Estimated duration of the task node in seconds, defaults to None.
        """
        self.name: str = name
        self.tasks: list[BaseTask[Any]] = (
            [tasks] if isinstance(tasks, BaseTask) else tasks
        )
        self.scoring_function = scoring_function or DefaultScoringFunction()
        self._logger = Logger(identifier=name, follow_logger_manager_rules=True)

        # Transitions to other nodes
        self.transitions: list[BaseTransition] = []

        # Internal state
        self.status: TaskStatus = TaskStatus.PENDING
        self.exceptions: list[Exception | None] = [None] * len(self.tasks)
        self.results: list[bool | None] = [None] * len(self.tasks)
        self.task_done: list[bool] = [False] * len(self.tasks)

        self.start_time: float | None = None
        self.end_time: float | None = None

        # Initialize points and estimated duration using tasks if not provided
        self.estimated_duration: float | Callable[[BaseGameContext], float] = None
        if estimated_duration is None:
            if all(
                isinstance(task.estimated_duration, (int, float)) for task in self.tasks
            ):
                self.estimated_duration = sum(
                    task.estimated_duration for task in self.tasks
                )
            else:
                self.estimated_duration = lambda ctx: sum(
                    task.estimated_duration(ctx)
                    if callable(task.estimated_duration)
                    else task.estimated_duration
                    for task in self.tasks
                )
        else:
            self.estimated_duration = estimated_duration

        self.points: int | Callable[[BaseGameContext], int] = None
        if points is None:
            if all(isinstance(task.points, int) for task in self.tasks):
                self.points = sum(task.points for task in self.tasks)
            else:
                self.points = lambda ctx: sum(
                    task.points(ctx) if callable(task.points) else task.points
                    for task in self.tasks
                )
        else:
            self.points = points

        self.entered = False
        self._exited = False

        self._logger.info(
            f"[STRAT:Task] Initialized '{self.name}' with {len(self.tasks)} task(s)",
        )

    def add_transition(self, transition: BaseTransition) -> None:
        """Add a transition to another task node.

        Args:
            transition (BaseTransition): Transition leading out of this node.
        """
        self.transitions.append(transition)
        self._logger.debug(
            f"[STRAT:Task] Added transition '{transition}' to '{self.name}'",
        )

    def score(self, prev_node: BaseTaskNode | None, ctx: BaseGameContext) -> float:
        """Compute a score for this node.

        Args:
            prev_node (BaseTaskNode | None): The previously executed node, if any.
            ctx (BaseGameContext): The current game context.

        Returns:
            float: The computed score value.
        """
        score_value = self.scoring_function.compute(
            prev_node=prev_node,
            current_node=self,
            ctx=ctx,
        )
        prev_name = prev_node.name if prev_node else "<None>"
        self._logger.debug(
            f"[STRAT:Task] '{self.name}' scored {score_value:.4f} vs '{prev_name}'",
        )
        return score_value

    def on_enter(self, prev_node: BaseTaskNode | None, _ctx: BaseGameContext) -> None:
        """Hook called when entering this node.

        Args:
            prev_node (BaseTaskNode | None): The node we are coming from.
            _ctx (BaseGameContext): The current game context.
        """
        prev_name = prev_node.name if prev_node else "<None>"
        self._logger.info(f"[STRAT:Task] Entering '{self.name}' from '{prev_name}'")

    def on_exit(self, next_node: BaseTaskNode | None, _ctx: BaseGameContext) -> None:
        """Hook called when exiting this node.

        Args:
            next_node (BaseTaskNode | None): The node that will be executed next.
            _ctx (BaseGameContext): The current game context.
        """
        next_name = next_node.name if next_node else "<None>"
        self._logger.info(f"[STRAT:Task] Exiting '{self.name}' to '{next_name}'")

    def _handle_task(self, idx: int, ctx: BaseGameContext) -> None:
        """Execute a single task and record its result.

        Args:
            idx (int): Index of the task to execute.
            ctx (BaseGameContext): The current game context.
        """
        task = self.tasks[idx]
        self._logger.debug(f"[STRAT:Task] Handling task {idx} of '{self.name}'")
        try:
            done = task.handle(ctx)
            self.results[idx] = done
            if done:
                self.task_done[idx] = True
                self._logger.info(
                    f"[STRAT:Task] Task {idx} of '{self.name}' completed",
                )
            else:
                self._logger.debug(
                    f"[STRAT:Task] Task {idx} of '{self.name}' not done yet",
                )
        except TimeoutError as e:
            self.exceptions[idx] = e
            self.task_done[idx] = True
            self._logger.warning(
                f"[STRAT:Task] Task {idx} of '{self.name}' timed out: {e}",
            )
        except Exception as e:  # noqa: BLE001
            self.exceptions[idx] = e
            self.task_done[idx] = True
            self._logger.error(
                f"[STRAT:Task] Task {idx} of '{self.name}' failed: {e}"
                f"\n{traceback.format_exc()}",
            )

    def execute(self, ctx: BaseGameContext) -> bool:
        """Execute tasks sequentially.

        Args:
            ctx (BaseGameContext): The current game context.

        Returns:
            bool: ``True`` when all tasks are completed, ``False`` otherwise.
        """
        if self.status in {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.TIMEOUT}:
            self._logger.debug(
                f"[STRAT:Task] '{self.name}' already completed: {self.status.name}",
            )
            return True

        if self.start_time is None:
            self.start_time = time.time()
            self.status = TaskStatus.IN_PROGRESS
            self._logger.info(f"[STRAT:Task] Started execution of '{self.name}'")

        # Handle only the first incomplete task per cycle
        try:
            next_idx = next(i for i, done in enumerate(self.task_done) if not done)
        except StopIteration:
            next_idx = None

        if next_idx is not None:
            self._handle_task(next_idx, ctx)

        if all(self.task_done):
            self.end_time = time.time()
            any_failed = any(
                (ex is not None) and not isinstance(ex, TimeoutError)
                for ex in self.exceptions
            )
            any_timeout = any(
                isinstance(ex, TimeoutError) for ex in self.exceptions if ex is not None
            )
            if any_failed:
                self.status = TaskStatus.FAILED
            elif any_timeout:
                self.status = TaskStatus.TIMEOUT
            else:
                self.status = TaskStatus.DONE

            elapsed = self.end_time - self.start_time
            self._logger.info(
                f"[STRAT:Task] Finished '{self.name}' {self.status.name} "
                f"in {elapsed:.2f}s",
            )
            return True

        return False

    def handle(self, ctx: BaseGameContext) -> bool:
        """Enter the node, execute tasks, and exit when finished.

        Args:
            ctx (BaseGameContext): The current game context.

        Returns:
            bool: ``True`` when all tasks are completed, ``False`` otherwise.
        """
        if not self.entered:
            self.on_enter(None, ctx)
            self.entered = True

        done = self.execute(ctx)

        if done and not self._exited:
            self.on_exit(None, ctx)
            self._exited = True

        return done

    __call__ = handle
