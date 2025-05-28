# ====== Local Project Imports ======
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
)

# ====== Internal Project Imports ======
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToConstruct,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    Backward,
)

from boombot_strategy.tasks.actuator_task.actuator_task import Build


def get_construct_sub_graph(zone_construct_id: int) -> BaseSubGraph:
    """
    Create a subgraph for navigating to a zone and performing a construction maneuver.

    This function builds a task graph consisting of:
    1. A node to navigate to the construction zone.
    2. A node to execute a backward maneuver for construction placement.
    The nodes are connected with a direct transition.

    Args:
        zone_construct_id (int): The identifier for the construction zone.

    Returns:
        BaseSubGraph: A compiled subgraph with defined entry and exit points.
    """
    construct_sub_graph = SubGraphBuilder()

    # Add node for navigating to the specified construction zone
    construct_sub_graph.add_node(
        f"[Construct] go to zone {zone_construct_id}",
        BaseTaskNode(
            f"[Construct] go to zone {zone_construct_id}",
            GoToColorReservedZoneToConstruct(zone_construct_id),
        ),
    )

    # Add node for actuators action of placing item
    construct_sub_graph.add_node(
        f"[Construct] placing item at zone {zone_construct_id}",
        BaseTaskNode(
            f"[Construct] placing item at zone {zone_construct_id}",
            Build(),
        ),
    )

    # Add node for precise backward motion to perform construction
    construct_sub_graph.add_node(
        f"[Construct] backward maneuver at zone {zone_construct_id}",
        BaseTaskNode(
            f"[Construct] backward maneuver at zone {zone_construct_id}", Backward(10)
        ),
    )

    construct_sub_graph.connect(
        f"[Construct] go to zone {zone_construct_id}",
        DirectTransition(
            construct_sub_graph.nodes(
                f"[Construct] placing item at zone {zone_construct_id}"
            )
        ),
    )

    construct_sub_graph.connect(
        f"[Construct] placing item at zone {zone_construct_id}",
        DirectTransition(
            construct_sub_graph.nodes(
                f"[Construct] backward maneuver at zone {zone_construct_id}"
            )
        ),
    )

    return construct_sub_graph.build(
        entry=f"[Construct] go to zone {zone_construct_id}",
        exits=f"[Construct] backward maneuver at zone {zone_construct_id}",
    )
