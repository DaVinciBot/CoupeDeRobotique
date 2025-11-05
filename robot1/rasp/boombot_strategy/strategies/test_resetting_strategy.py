"""Primary tower rush strategy focusing on rapid construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs.deplacement import get_deplacement_subgraph
from boombot_strategy.sub_graphs.resetting import get_resetting_subgraph
from strategy.core import GraphRunner

if TYPE_CHECKING:
    from boombot_strategy.show_game_context import ShowGameContext


class TestResettingStrategy(BaseStrategy):
    """Execute a tower rush with pick-up, build, and push phases.

    - Deploy banner
    - Perform one pickup and construction cycle
    - Perform one pickup-to-placement cycle
    - Navigate to backstage zone to finish the game
    """

    def __init__(self, ctx: ShowGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (ShowGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        deplacement_subgraph = get_deplacement_subgraph(zone_id=9)

        resetting_subgraph = get_resetting_subgraph()

        deplacement_subgraph1 = get_deplacement_subgraph(zone_id=20)

        resetting_subgraph1 = get_resetting_subgraph()

        deplacement_subgraph2 = get_deplacement_subgraph(zone_id=11)

        resetting_subgraph2 = get_resetting_subgraph()

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            deplacement_subgraph,
            resetting_subgraph,
            deplacement_subgraph1,
            resetting_subgraph1,
            deplacement_subgraph2,
            resetting_subgraph2,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="ResettingTestRunner",
                follow_logger_manager_rules=True,
            ),
            start=deplacement_subgraph.get_entry(),
        )
