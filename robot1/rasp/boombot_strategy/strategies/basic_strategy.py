from loggerplusplus import Logger
from boombot_strategy import ShowGameContext
from boombot_strategy.sub_graphs import get_pickup_sub_graph, get_construct_sub_graph
from boombot_strategy.strategies import BaseStrategy
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)

from boombot_strategy.tasks.navigation_tasks.maneuver import PreciseForward, Backward
from boombot_strategy.tasks.actuator_task.actuator_task import BlockBanner
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
    GraphRunner,
)

from strategy.tools import (
    visualize_task_graph_from_node,
    visualize_task_graph,
    visualize_entire_subgraph,
)


class BasicStrategy(BaseStrategy):
    def __init__(self, ctx: ShowGameContext):
        super().__init__(ctx)

        block_banner = BaseTaskNode(
            name="Block Banner",
            tasks=BlockBanner(),
        )

        precise_forward_to_deploy_brand = BaseTaskNode(
            name="Precise forward to deploy brand",
            tasks=PreciseForward(7),
        )

        backward_to_extract_from_deploy_brand = BaseTaskNode(
            name="Backward to extract from deploy brand",
            tasks=Backward(15),
        )

        block_banner.add_transition(DirectTransition(precise_forward_to_deploy_brand))

        precise_forward_to_deploy_brand.add_transition(
            DirectTransition(backward_to_extract_from_deploy_brand)
        )

        first_pickup_zone = get_pickup_sub_graph(self.zones["first_pickup_zone"], ctx)
        first_build_zone = get_construct_sub_graph(
            self.zones["first_build_zone"], ctx, 6
        )

        backward_to_extract_from_deploy_brand.add_transition(
            DirectTransition(first_pickup_zone.get_entry())
        )

        first_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(first_build_zone.get_entry())
        )

        second_pickup_zone = get_pickup_sub_graph(self.zones["second_pickup_zone"], ctx)
        second_build_zone = get_construct_sub_graph(
            self.zones["second_build_zone"], ctx
        )
        second_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(second_build_zone.get_entry())
        )

        third_pickup_zone = get_pickup_sub_graph(self.zones["third_pickup_zone"], ctx)
        third_build_zone = get_construct_sub_graph(
            self.zones["first_build_zone"], ctx, 0
        )
        third_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(third_build_zone.get_entry())
        )

        # fourth_pickup_zone = get_pickup_sub_graph(self.zones["fourth_pickup_zone"], ctx)
        # fourth_build_zone = get_construct_sub_graph(
        #     self.zones["first_build_zone"], ctx, -2.5
        # )
        # fourth_pickup_zone.get_exits()[0].add_transition(
        #     DirectTransition(fourth_build_zone.get_entry())
        # )

        go_to_backstage = BaseTaskNode(
            name="Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"]),
        )

        first_build_zone.get_exits()[0].add_transition(
            DirectTransition(second_pickup_zone.get_entry())
        )
        second_build_zone.get_exits()[0].add_transition(
            DirectTransition(third_pickup_zone.get_entry())
        )
        third_build_zone.get_exits()[0].add_transition(
            DirectTransition(go_to_backstage)
        )

        self.runner = GraphRunner(
            logger=Logger(
                identifier="BasicStrategyRunner", follow_logger_manager_rules=True
            ),
            start=block_banner,
        )
