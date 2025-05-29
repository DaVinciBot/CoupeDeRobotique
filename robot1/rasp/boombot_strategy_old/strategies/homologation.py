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
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=40, width_view=40
            ),
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
            avoidance_params=StopAndWaitAvoidanceParams(timeout=30),
            acs_detection_profile_params=RectangularProjectionAcsDetectionProfileParams(
                acs_distance=40, width_view=40
            ),
        )


# ================ Create Logic Graph ================
# 1. Create nodes
go_straight_node = BaseTaskNode("GoStraight 230", GoStraight(distance=230))
rotate_node = BaseTaskNode("Rotate 180", Rotate(theta=math.pi))


# 2. Connect nodes
go_straight_node.add_transition(DirectTransition(rotate_node))

# 3. Create Graph runner
homologation_runner = GraphRunner(start=go_straight_node, parallel=False)
