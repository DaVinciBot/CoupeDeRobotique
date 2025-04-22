from boombot_strategy.show_game_context import ShowGameContext

from boombot_strategy.sub_graphs import get_pickup_sub_graph, get_construct_sub_graph

from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
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
yellow_strategy.add_subgraph(pickup_zone_4)
yellow_strategy.add_subgraph(construct_zone_11)

yellow_strategy.connect(
    from_name=pickup_zone_4.get_exits()[0].name,
    transition=DirectTransition(construct_zone_11.get_entry()),
)

built_graph = yellow_strategy.build(
    entry=pickup_zone_4.get_entry(),
    exits=construct_zone_11.get_exits(),
)


visualize_task_graph_from_node(
    subgraph=built_graph,
    title="Yellow Strategy",
)
