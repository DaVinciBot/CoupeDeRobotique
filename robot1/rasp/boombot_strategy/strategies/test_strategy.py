from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import get_cursor_alignment_forward_subgraph
from geometry import OrientedPoint
from log_manager import LogLogger
from strategy.core import GraphRunner

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
        self.pickup_zones = CONFIG.PICKUP_ZONES
        self.pickup_zones_list = CONFIG.PICKUP_ZONES_LIST
        self.deposit_zones = CONFIG.DEPOSIT_ZONES
        self.deposit_zones_list = CONFIG.DEPOSIT_ZONES_LIST
        self.color_zone = CONFIG.TEAM_SPECIFIC_ZONES[ctx.arena.team_color.value]

        deposit_subgraph = get_cursor_alignment_forward_subgraph(
            OrientedPoint(100, 100, 0),
            ctx,
        )

        self._auto_build_transitions(deposit_subgraph)

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="TestStrategy",
                follow_logger_manager_rules=True,
            ),
            start=deposit_subgraph.get_entry(),
        )
