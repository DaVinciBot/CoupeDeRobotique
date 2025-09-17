"""Strategy that only deploys the banner before finishing."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import get_banner_deployment_subgraph
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from boombot_strategy.show_game_context import ShowGameContext


class OnlyBannerStrategy(BaseStrategy):
    """Deploy the banner then move directly to the backstage zone."""

    def __init__(self, ctx: ShowGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (ShowGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        # Step 1: Deploy the banner
        deploy_banner_subgraph = get_banner_deployment_subgraph()

        # Step 2: Move to the backstage zone to finish the game
        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"]),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(deploy_banner_subgraph, go_to_backstage)

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="OnlyBannerStrategy",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
