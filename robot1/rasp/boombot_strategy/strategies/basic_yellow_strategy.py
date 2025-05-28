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
