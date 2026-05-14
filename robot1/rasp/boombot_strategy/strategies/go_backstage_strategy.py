"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import RelativeForward, RelativeRotation, RelativeBackward
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


class GoBackstageStrategy(BaseStrategy):
    """Deploy the banner then move directly to the backstage zone."""

    def __init__(self, ctx: WinterGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        forward = BaseTaskNode(
            name="Move Forward",
            tasks=RelativeForward(distance=20.0),
        )

        backward = BaseTaskNode(
            name="Move Backward",
            tasks=RelativeBackward(distance=20.0),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(forward, backward)

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="GoBackstageStrategy",
                follow_logger_manager_rules=True,
            ),
            start=forward,
        )
