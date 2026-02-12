"""Primary tower rush strategy focusing on rapid construction."""

from __future__ import annotations

from typing import TYPE_CHECKING

from old_boombot_strategy.strategies.base_strategy import BaseStrategy
from old_boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_construct_subgraph,
    get_pickup_subgraph,
    get_push_one_floor_to_wall_subgraph,
)
from old_boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)

from log_manager import LogLogger
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode

if TYPE_CHECKING:
    from old_boombot_strategy.show_game_context import ShowGameContext


class TowerRushStrategy(BaseStrategy):
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

        # Step 1: Deploy the banner
        deploy_banner_subgraph = get_banner_deployment_subgraph()

        # Step 2: Navigate to the first pickup zone
        first_pickup_subgraph = get_pickup_subgraph(self.zones["first_pickup_zone"])

        # Step 3: Navigate to the first construction zone
        first_construct_subgraph = get_construct_subgraph(
            self.zones["first_build_zone"],
            back_offset=13,
        )

        # Step 4:
        second_pickup_subgraph = get_push_one_floor_to_wall_subgraph(
            zone_id=self.zones["second_pickup_zone"],
            push_distance=30,
        )

        # Step 6: Move to the backstage zone to finish the game
        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"]),
        )

        # Connect the subgraphs in execution order
        self._auto_build_transitions(
            deploy_banner_subgraph,
            first_pickup_subgraph,
            first_construct_subgraph,
            second_pickup_subgraph,
            go_to_backstage,
        )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="TowerRushStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
