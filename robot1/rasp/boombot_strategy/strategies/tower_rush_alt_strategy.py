# ====== Code Summary ======
# This module defines the `TowerRushStrategy` class, which extends `TowerRushStrategy` and orchestrates
# the full game flow for a robot. The strategy consists of deploying a banner, picking up items,
# constructing structures, and finally moving to a backstage zone to complete the game.
# It uses task subgraphs and direct transitions to sequence actions through a `GraphRunner`.

from loggerplusplus import Logger

from boombot_strategy import ShowGameContext
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_banner_deployment_subgraph,
    get_construct_one_floor_subgraph,
    get_construct_subgraph,
    get_pickup_subgraph,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from strategy.core import (
    BaseTaskNode,
    GraphRunner,
)


class TowerRushAltStrategy(BaseStrategy):
    """Defines the tower rush game strategy by sequencing multiple subgraphs:
    - Deploy banner
    - Perform one pickup and construction cycle
    - Perform one pickup-to-placement cycle
    - Navigate to backstage zone to finish the game
    """

    def __init__(self, ctx: ShowGameContext):
        """Initialize the strategy with the required task flow using subgraphs and direct transitions.

        Args:
            ctx (ShowGameContext): Game context containing game-specific configurations and zones.
        """
        super().__init__(ctx)

        # Step 1: Deploy the banner
        deploy_banner_subgraph = get_banner_deployment_subgraph()

        # Step 2: Navigate to the first pickup zone
        first_pickup_subgraph = get_pickup_subgraph(self.zones["first_pickup_zone"])

        # Step 3: Navigate to the first construction zone
        first_construct_subgraph = get_construct_subgraph(
            self.zones["first_build_zone"], back_offset=5,
        )

        # Step 4: Navigate to the second pickup zone
        second_pickup_subgraph = get_pickup_subgraph(self.zones["second_pickup_zone"])

        # Step 5: Navigate to the second construction zone
        second_construct_subgraph = get_construct_one_floor_subgraph(
            self.zones["second_build_zone"], back_offset=15,
        )

        # Step 6: Navigate to the second pickup zone
        third_pickup_subgraph = get_pickup_subgraph(self.zones["third_pickup_zone"])

        # Step 7: Navigate to the second construction zone
        third_construct_subgraph = get_construct_one_floor_subgraph(
            self.zones["first_build_zone"], back_offset=18,
        )

        # Step 8 Move to the backstage zone to finish the game
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
