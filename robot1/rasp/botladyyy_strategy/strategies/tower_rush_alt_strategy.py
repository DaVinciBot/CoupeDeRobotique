"""Alternate tower rush strategy using multiple pickup cycles."""

from __future__ import annotations

from typing import TYPE_CHECKING

from loggerplusplus import Logger

from botladyyy_strategy.strategies.base_strategy import BaseStrategy
from botladyyy_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_construct_one_floor_subgraph,
    get_construct_subgraph,
    get_pickup_subgraph,
)
from botladyyy_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from botladyyy_strategy.winter_game_context import WinterGameContext


class TowerRushAltStrategy(BaseStrategy):
    """Execute a tower rush with additional pickup cycles.

    - Deploy banner
    - Perform one pickup and construction cycle
    - Perform one pickup-to-placement cycle
    - Navigate to backstage zone to finish the game
    """

    def __init__(self, ctx: WinterGameContext) -> None:
        """Initialize the strategy.

        Build the task flow using subgraphs and direct transitions.

        Args:
            ctx (WinterGameContext):
                Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        # Step 1: Deploy the banner
        deploy_banner_subgraph = get_banner_deployment_subgraph()

        # Step 2: Navigate to the first pickup zone
        first_pickup_subgraph = get_pickup_subgraph(
            self.zones["first_pickup_zone"],
            ctx,
        )

        # Step 3: Navigate to the first construction zone
        first_construct_subgraph = get_construct_subgraph(
            self.zones["first_build_zone"],
            ctx,
            back_offset=5,
        )

        # Step 4: Navigate to the second pickup zone
        second_pickup_subgraph = get_pickup_subgraph(
            self.zones["second_pickup_zone"],
            ctx,
        )

        # Step 5: Navigate to the second construction zone
        second_construct_subgraph = get_construct_one_floor_subgraph(
            self.zones["second_build_zone"],
            ctx,
            back_offset=15,
        )

        # Step 6: Navigate to the second pickup zone
        third_pickup_subgraph = get_pickup_subgraph(
            self.zones["third_pickup_zone"],
            ctx,
        )

        # Step 7: Navigate to the first construction zone
        third_construct_subgraph = get_construct_one_floor_subgraph(
            self.zones["first_build_zone"],
            ctx,
            back_offset=18,
        )

        # Step 8 Move to the backstage zone to finish the game
        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"], ctx),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            deploy_banner_subgraph,
            first_pickup_subgraph,
            first_construct_subgraph,
            second_pickup_subgraph,
            second_construct_subgraph,
            third_pickup_subgraph,
            third_construct_subgraph,
            go_to_backstage,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="TowerRushStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
