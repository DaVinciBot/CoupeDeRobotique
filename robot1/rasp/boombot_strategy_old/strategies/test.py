# External import
from math import pi

from config_loader import CONFIG

# Common imports
from strategy.core import (
    BaseTaskNode,
    SubGraphBuilder,
    DirectTransition,
    ConditionalTransition,
    GraphRunner,
)

from strategy.tools import visualize_task_graph


# Local imports
from boombot_strategy.show_game_context import ShowGameContext
from boombot_strategy.tasks.navigation_tasks.utils import GoStraight, Rotate

# Create nodes
go_straight_node_40 = BaseTaskNode("GoStraight 40", GoStraight(distance=40))
go_straight_node_50 = BaseTaskNode("GoStraight 50", GoStraight(distance=50))
rotate_node_90 = BaseTaskNode("Rotate 90", Rotate(theta=pi / 2))
rotate_node_180 = BaseTaskNode("Rotate 180", Rotate(theta=pi))

# Create transitions
go_straight_node_40.add_transition(DirectTransition(rotate_node_90))
rotate_node_90.add_transition(DirectTransition(go_straight_node_50))
go_straight_node_50.add_transition(DirectTransition(rotate_node_180))

# Run graph
demo_runner = GraphRunner(start=go_straight_node_40, parallel=False)
