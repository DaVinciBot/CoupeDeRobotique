from __future__ import annotations
from typing import TYPE_CHECKING
from typing import Callable, List, Optional
from strategy.core.tasks import BaseTask

from strategy.core.base_game_context import BaseGameContext
from enum import Enum, auto
import time

from strategy.core.tasks import TaskStatus
from strategy.core.task_nodes.scoring_functions import (
    BaseScoringFunction,
    DefaultScoringFunction,
)


if TYPE_CHECKING:
    from strategy.core.transitions import BaseTransition


class BaseTaskNode:
    def __init__(
        self,
        name: str,
        task: list[BaseTask] | BaseTask,
        scoring_function: BaseScoringFunction = DefaultScoringFunction(),
    ) -> None:
        self.name: str = name
        self.tasks: list[BaseTask] = task if isinstance(task, list) else [task]
        self.scoring_function: BaseScoringFunction = scoring_function

        # Transitions
        self.transitions: List[BaseTransition] = []

        # Internal state
        self.status: TaskStatus = TaskStatus.PENDING
        self.exceptions: List[Optional[Exception]] = [None] * len(self.tasks)
        self.results: List[Optional[bool]] = [None] * len(self.tasks)
        self.task_done: List[bool] = [False] * len(self.tasks)

        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        self._entered = False
        self._exited = False

    def add_transition(self, transition: BaseTransition) -> None:
        self.transitions.append(transition)

    def score(self, prev: BaseTaskNode, ctx: BaseGameContext) -> float:
        return self.scoring_function.compute(prev_node=prev, current_node=self, ctx=ctx)

    def on_enter(self, prev: Optional[BaseTaskNode], ctx: BaseGameContext) -> None:
        pass

    def on_exit(self, next_node: Optional[BaseTaskNode], ctx: BaseGameContext) -> None:
        pass

    def execute(self, ctx: BaseGameContext) -> bool:
        """
        Exécute les tâches en parallèle – retourne True uniquement si toutes sont terminées.
        """
        if self.status in {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.TIMEOUT}:
            return True

        if self.start_time is None:
            self.start_time = time.time()
            self.status = TaskStatus.IN_PROGRESS

        all_done = True
        any_failed = False
        any_timeout = False

        for i, task in enumerate(self.tasks):
            if self.task_done[i]:
                continue

            try:
                done = task.handle(ctx)
                self.results[i] = done
                if done:
                    self.task_done[i] = True
                else:
                    all_done = False

            except TimeoutError as e:
                self.exceptions[i] = e
                self.task_done[i] = True
                any_timeout = True

            except Exception as e:
                self.exceptions[i] = e
                self.task_done[i] = True
                any_failed = True

        if all(self.task_done):
            self.end_time = time.time()
            if any_failed:
                self.status = TaskStatus.FAILED
            elif any_timeout:
                self.status = TaskStatus.TIMEOUT
            else:
                self.status = TaskStatus.DONE
            return True

        return False

    def handle(self, ctx: BaseGameContext) -> bool:
        if not self._entered:
            self.on_enter(None, ctx)
            self._entered = True

        done = self.execute(ctx)

        if done and not self._exited:
            self.on_exit(None, ctx)
            self._exited = True

        return done

    __call__ = handle
