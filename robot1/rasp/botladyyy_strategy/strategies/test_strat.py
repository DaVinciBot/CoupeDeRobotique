"""Alternate tower rush strategy using multiple pickup cycles."""

from __future__ import annotations

import math
from typing import TYPE_CHECKING

from botladyyy_strategy.strategies.base_strategy import BaseStrategy
from botladyyy_strategy.tasks.navigation_tasks.maneuver import RelativeRotation
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from botladyyy_strategy.winter_game_context import WinterGameContext


class TestStrategy(BaseStrategy):
    """Execute a tower rush with additional pickup cycles."""

    def __init__(self, ctx: WinterGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        task = BaseTaskNode("rotation", RelativeRotation(angle=math.pi))

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            task,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="TestStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=task,
        )
