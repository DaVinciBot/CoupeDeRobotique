from loggerplusplus import Logger
from boombot_strategy import ShowGameContext
from boombot_strategy.sub_graphs import get_pickup_sub_graph, get_construct_sub_graph
from boombot_strategy.strategies import BaseStrategy

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

        first_pickup_zone = get_pickup_sub_graph(self.zones["first_pickup_zone"], ctx)
        first_build_zone = get_construct_sub_graph(self.zones["first_build_zone"], ctx)
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
        third_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(first_build_zone.get_entry())
        )

        fourth_pickup_zone = get_pickup_sub_graph(self.zones["fourth_pickup_zone"], ctx)
        fourth_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(first_build_zone.get_entry())
        )

        first_build_zone.get_exits()[0].add_transition(
            DirectTransition(second_pickup_zone.get_entry())
        )
        first_build_zone.get_exits()[0].add_transition(
            DirectTransition(third_pickup_zone.get_entry())
        )
        first_build_zone.get_exits()[0].add_transition(
            DirectTransition(fourth_pickup_zone.get_entry())
        )

        second_build_zone.get_exits()[0].add_transition(
            DirectTransition(first_pickup_zone.get_entry())
        )
        second_build_zone.get_exits()[0].add_transition(
            DirectTransition(third_pickup_zone.get_entry())
        )
        second_build_zone.get_exits()[0].add_transition(
            DirectTransition(fourth_pickup_zone.get_entry())
        )

        self.runner = GraphRunner(
            logger=Logger(
                identifier="BasicStrategyRunner", follow_logger_manager_rules=True
            ),
            start=first_pickup_zone.get_entry(),
        )
