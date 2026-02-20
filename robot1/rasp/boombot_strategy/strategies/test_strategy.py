from __future__ import annotations

from typing import TYPE_CHECKING

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_pickup_jenga_subgraph,
    get_deposit_jenga_color_zone_subgraph,
    get_deposit_jenga_deposit_zone_subgraph,
    get_cursor_alignment_backward_subgraph,
    get_cursor_alignment_forward_subgraph,
)

from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


class TestStrategy(BaseStrategy):
    """Test strategy for validating task execution and transitions."""

    def __init__(self, ctx: WinterGameContext) -> None:
        """Initialize the test strategy.

        Build a simple task flow to test navigation and actuator tasks.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        get_jenga_subgraph = get_pickup_jenga_subgraph(self.zones[0])

        self._auto_build_transitions(
                get_jenga_subgraph,
        )

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="TestStrategy",
                follow_logger_manager_rules=True,
            ),
            start=get_jenga_subgraph.get_entry(),
        )



