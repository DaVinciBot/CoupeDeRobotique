from __future__ import annotations
from abc import ABC, abstractmethod


from typing import TYPE_CHECKING


from strategy.core.base_game_context import BaseGameContext


if TYPE_CHECKING:
    from strategy.core.task_nodes.base_task_node import BaseTaskNode

from strategy.core.task_nodes.scoring_functions.base_scoring_function import (
    BaseScoringFunction,
)


class NavigationScoringFunction(BaseScoringFunction):
    def __init__(self, distance: float):
        self.distance = distance
        
    def compute(
        self, prev_node: BaseTaskNode, current_node: BaseTaskNode, ctx: BaseGameContext
    ) -> float:
        return max(0.0, (1.0 - self.distance / 200.0) * 6.0)


