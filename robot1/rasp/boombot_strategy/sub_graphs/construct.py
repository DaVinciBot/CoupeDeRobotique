# ====== Code Summary ======
# This module defines a function `get_construct_subgraph` that builds a task subgraph
# for performing a construction sequence in a specified zone. The sequence includes
# navigation to the construction zone, a preparatory forward movement, actuator-based
# item placement, and a final backward maneuver. Tasks are connected via direct transitions
# and returned as a `BaseSubGraph` for integration into a larger strategy graph.

# ====== Local Project Imports ======
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
)

# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToConstruct,
)
from boombot_strategy.tasks.navigation_tasks import RelativeForward, RelativeBackward
from boombot_strategy.tasks.actuator_task import Build


def get_construct_subgraph(zone_id: int, back_offset: int = 0) -> BaseSubGraph:
    """
    Construct a subgraph for a robot to perform a construction task at a specified zone.

    The subgraph includes navigation to the zone, positioning forward, item placement using actuators,
    and a backward maneuver for precise alignment or disengagement.

    Args:
        zone_id (int): Identifier for the target construction zone.
        back_offset (int, optional): Distance already covered behind the zone, used to adjust forward motion.

    Returns:
        BaseSubGraph: A compiled subgraph that defines the sequence of construction-related tasks.
    """
    subgraph = SubGraphBuilder()

    # Node: Navigate to construction zone
    node_navigate = f"[Construct] Navigate to zone {zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToColorReservedZoneToConstruct(zone_id),
        ),
    )

    # Node: Move forward to prepare for placement
    node_prepare = f"[Construct] Position at zone {zone_id}"
    subgraph.add_node(
        node_prepare,
        BaseTaskNode(
            name=node_prepare,
            tasks=RelativeForward(18 - back_offset),
        ),
    )

    # Node: Place item with actuators
    node_place = f"[Construct] Place item at zone {zone_id}"
    subgraph.add_node(
        node_place,
        BaseTaskNode(name=node_place, tasks=Build()),
    )

    # Node: Perform backward maneuver after placement
    node_back = f"[Construct] Backward from zone {zone_id}"
    subgraph.add_node(
        node_back,
        BaseTaskNode(name=node_back, tasks=RelativeBackward(20)),
    )

    # Transitions between nodes
    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_prepare]))
    subgraph.connect(node_prepare, DirectTransition(subgraph.nodes[node_place]))
    subgraph.connect(node_place, DirectTransition(subgraph.nodes[node_back]))

    # Return compiled subgraph with defined entry and exit
    return subgraph.build(
        entry=node_navigate,
        exits=node_back,
    )
