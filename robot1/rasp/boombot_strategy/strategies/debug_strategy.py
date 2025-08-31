"""Debug strategy executing a minimal set of actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_pickup_subgraph,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from strategy.core import BaseTaskNode, GraphRunner

if TYPE_CHECKING:
    from boombot_strategy import ShowGameContext


class DebugStrategy(BaseStrategy):
    """Define a minimal game strategy for debugging.

    - Deploy banner
    - Perform two pickup and construction cycles
    - Navigate to backstage zone to finish the game

    """

    def __init__(self, ctx: ShowGameContext) -> None:
        """Initialize the strategy with the required task flow using subgraphs and direct transitions.

        Args:
            ctx (ShowGameContext):
                Game context containing game-specific configurations and zones.

        """
        super().__init__(ctx)

        # Step 1: Deploy the banner
        deploy_banner_subgraph = get_banner_deployment_subgraph()

        # Step 2: Navigate to the first pickup zone
        first_pickup_subgraph = get_pickup_subgraph(self.zones["first_pickup_zone"])

        # Step 6: Move to the backstage zone to finish the game
        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"]),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            deploy_banner_subgraph,
            first_pickup_subgraph,
            go_to_backstage,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="BasicStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
