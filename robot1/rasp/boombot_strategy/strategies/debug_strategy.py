"""Debug strategy executing a minimal set of actions."""

from __future__ import annotations

from typing import TYPE_CHECKING

from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_pickup_subgraph,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from strategy.core.base_game_context import BaseGameContext


class DebugStrategy(BaseStrategy):
    """Define a minimal game strategy for debugging.

    - Deploy banner
    - Perform two pickup and construction cycles
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
            logger=LogLogger(
                identifier="BasicStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
