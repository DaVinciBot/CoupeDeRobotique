from boombot_strategy.show_game_context import ShowGameContext
from loggerplusplus import Logger
from boombot_strategy.sub_graphs import get_pickup_sub_graph, get_construct_sub_graph

from config_loader import CONFIG
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
import math
from navigation import (
    NoAvoidanceParams,
    DeltaPathPlannerParams,
    SequentialTrajectoryPlannerParams,
    Direction,
    StopAndWaitAvoidanceParams
)
from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask

# ================ Create Task dedicated to homolagation ================
class GoStraight(NavigationTask):
    def __init__(self, distance: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(distance=distance),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.FORWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(),
        )
class Rotate(NavigationTask):
    def __init__(self, theta: float):
        super().__init__(
            goal=None,
            path_planner_params=DeltaPathPlannerParams(rotation=theta),
            trajectory_planner_params=SequentialTrajectoryPlannerParams(
                direction=Direction.FORWARD
            ),
            speed_profiler=CONFIG.ROLLING_BASIS_DEFAULT_SPEED_PROFILER,
            avoidance_params=StopAndWaitAvoidanceParams(),
        )
      
# ================ Create Logic Graph ================  
homologation_graph = SubGraphBuilder()

# 1. Create nodes
homologation_graph.add_node(
    "Go forward",
    BaseTaskNode("Go forward", GoStraight(50))
)
homologation_graph.add_node(
    "Return",
    BaseTaskNode("Return", Rotate(math.pi))
)
homologation_graph.add_node(
    "Go home",
    BaseTaskNode("Go home", GoStraight(50))
)

# 2. Connect nodes
homologation_graph.connect(
    "Go forward", DirectTransition("Return")
)
homologation_graph.connect(
    "Return", DirectTransition("Go home")
)

# 3. Build the graph 
built_homologation_graph = homologation_graph.build(
    entry="Go forward",
    exits="Return",
)

# 4. Create Graph runner

yellow_strategy_runner = GraphRunner(
    logger=Logger(identifier="HomologationRunner", follow_logger_manager_rules=True),
    start=built_homologation_graph.get_entry(),
)
