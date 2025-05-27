from boombot_strategy.show_game_context import ShowGameContext
from loggerplusplus import Logger
from boombot_strategy.sub_graphs import get_pickup_sub_graph, get_construct_sub_graph

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


yellow_strategy = SubGraphBuilder()

# Start by pickup zone 4, then construct to zone 11
pickup_zone_4 = get_pickup_sub_graph(4)
construct_zone_11 = get_construct_sub_graph(11)

pickup_zone_4.get_exits()[0].add_transition(
    DirectTransition(construct_zone_11.get_entry())
)


yellow_strategy_runner = GraphRunner(
    logger=Logger(identifier="YellowStrategyRunner", follow_logger_manager_rules=True),
    start=pickup_zone_4.get_entry(),
)


visualize_task_graph_from_node(
    subgraph=pickup_zone_4,
    title="Pickup Zone",
)
