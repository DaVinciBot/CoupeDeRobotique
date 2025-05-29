from loggerplusplus import Logger
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
    def __init__(self, color: str):
        super().__init__(color)

        self.first_pickup_zone = get_pickup_sub_graph(self.zones["first_pickup_zone"])
        self.first_construct_zone = get_construct_sub_graph(
            self.zones["first_construct_zone"]
        )
        self.first_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(self.first_construct_zone.get_entry())
        )

        self.second_pickup_zone = get_pickup_sub_graph(self.zones["second_pickup_zone"])
        self.second_construct_zone = get_construct_sub_graph(
            self.zones["second_construct_zone"]
        )
        self.second_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(self.second_construct_zone.get_entry())
        )

        self.third_pickup_zone = get_pickup_sub_graph(self.zones["third_pickup_zone"])
        self.third_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(self.first_construct_zone.get_entry())
        )

        self.fourth_pickup_zone = get_pickup_sub_graph(self.zones["fourth_pickup_zone"])
        self.fourth_pickup_zone.get_exits()[0].add_transition(
            DirectTransition(self.first_construct_zone.get_entry())
        )

        self.first_construct_zone.get_exits()[0].add_transition(
            DirectTransition(self.second_pickup_zone.get_entry())
        )

        self.runner = GraphRunner(
            logger=Logger(
                identifier="BasicStrategyRunner", follow_logger_manager_rules=True
            ),
            start=self.first_pickup_zone.get_entry(),
        )
