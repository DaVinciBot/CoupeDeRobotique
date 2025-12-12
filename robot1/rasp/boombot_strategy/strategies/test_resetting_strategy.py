"""Primary tower rush strategy focusing on rapid construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs.deplacement import get_deplacement_subgraph
from boombot_strategy.sub_graphs.resetting import get_resetting_subgraph
from strategy.core import GraphRunner

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext


class TestResettingStrategy(BaseStrategy):
    """Execute a tower rush with pick-up, build, and push phases.

    - Deploy banner
    - Perform one pickup and construction cycle
    - Perform one pickup-to-placement cycle
    - Navigate to backstage zone to finish the game
    """

    def __init__(self, ctx: BaseGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (BaseGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        deplacement_subgraph = get_deplacement_subgraph(zone_id=1)

        resetting_subgraph = get_resetting_subgraph()

        deplacement_subgraph1 = get_deplacement_subgraph(zone_id=2)

        resetting_subgraph1 = get_resetting_subgraph()

        deplacement_subgraph2 = get_deplacement_subgraph(zone_id=8)

        resetting_subgraph2 = get_resetting_subgraph()

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            resetting_subgraph,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="ResettingTestRunner",
                follow_logger_manager_rules=True,
            ),
            start=resetting_subgraph.get_entry(),
        )
