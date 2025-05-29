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
    StopAndWaitAvoidanceParams,
)

from navigation.avoidance.acs_detection_profiles import (
    NoProjectionAcsDetectionProfileParams,
    RectangularProjectionAcsDetectionProfileParams,
)

from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)

from boombot_strategy.tasks.navigation_tasks.navigation_task import NavigationTask

# ================ Create Logic Graph ================
# 1. Go to Zone

# 1. Create nodes
go_zone_9_to_pickup = BaseTaskNode("go_zone_9_to_pickup", GoToStuffZoneToPickUp(9))




yellow_hardcode_strategy = GraphRunner(start=go_zone_9_to_pickup, parallel=False)
