from __future__ import annotations
from typing import TYPE_CHECKING

import time
from typing import Optional, List
from strategy.core.task_nodes.base_task_node import BaseTaskNode
from strategy.core.tasks.base_task import BaseTask
from strategy.core.base_game_context import BaseGameContext
from strategy.core.task_nodes.scoring_functions import (
    BaseScoringFunction,
    DefaultScoringFunction,
)
from strategy.core.tasks import TaskStatus


class TimeoutTaskNode(BaseTaskNode):
    def __init__(
        self,
        name: str,
        task: BaseTask | List[BaseTask],
        timeout_seconds: float,
        scoring_function: BaseScoringFunction = DefaultScoringFunction(),
    ) -> None:
        super().__init__(name, task, scoring_function)
        self.timeout_seconds = timeout_seconds
        self._timeout_triggered = False

    def on_timeout(self, ctx: BaseGameContext) -> None:
        """Hook appelé une seule fois quand un timeout est déclenché."""
        pass  # surcharge dans les classes filles si besoin

    def execute(self, ctx: BaseGameContext) -> bool:
        if self.status in {TaskStatus.DONE, TaskStatus.FAILED, TaskStatus.TIMEOUT}:
            return True

        now = time.time()

        # première exécution
        if self.start_time is None:
            self.start_time = now
            self.status = TaskStatus.IN_PROGRESS

        elapsed = now - self.start_time
        if elapsed >= self.timeout_seconds:
            if not self._timeout_triggered:
                self.on_timeout(ctx)
                self._timeout_triggered = True
            self.status = TaskStatus.TIMEOUT
            self.end_time = now
            return True  # Timeout atteint, arrêt immédiat

        return super().execute(ctx)
