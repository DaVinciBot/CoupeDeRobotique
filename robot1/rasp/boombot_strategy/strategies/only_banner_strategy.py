# ====== Code Summary ======
# This module defines the `BasicStrategy` class, which extends `BaseStrategy` and orchestrates
# the full game flow for a robot. The strategy consists of deploying a banner, picking up items,
# constructing structures, and finally moving to a backstage zone to complete the game.
# It uses task subgraphs and direct transitions to sequence actions through a `GraphRunner`.

# ====== Local Project Imports ======
from loggerplusplus import Logger
from strategy.core import (
    BaseTaskNode,
    DirectTransition,
    GraphRunner,
)

# ====== Internal Project Imports ======
from boombot_strategy import ShowGameContext
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.sub_graphs import (
    get_construct_subgraph,
    get_pickup_subgraph,
    get_banner_deployment_subgraph,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)


class OnlyBannerStrategy(BaseStrategy):
    """
    Defines a basic game strategy by sequencing multiple subgraphs:
    - Deploy banner
    - Perform two pickup and construction cycles
    - Navigate to backstage zone to finish the game
    """

    def __init__(self, ctx: ShowGameContext):
        """
        Initialize the strategy with the required task flow using subgraphs and direct transitions.

        Args:
            ctx (ShowGameContext): Game context containing game-specific configurations and zones.
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
        # deploy_banner_subgraph.get_exits()[0].add_transition(
        #     DirectTransition(go_to_backstage)
        # )

        # Create the graph runner starting from the first subgraph
        self.runner = GraphRunner(
            logger=Logger(
                identifier="OnlyBannerStrategy",
                follow_logger_manager_rules=True,
            ),
            start=deploy_banner_subgraph.get_entry(),
        )
