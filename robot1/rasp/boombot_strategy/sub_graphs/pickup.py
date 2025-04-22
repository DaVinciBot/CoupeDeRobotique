# ====== Local Project Imports ======
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
)

# ====== Internal Project Imports ======
from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    PreciseForward,
)


def get_pickup_sub_graph(zone_pickup_id: int) -> BaseSubGraph:
    """
    Create a subgraph for navigating to a zone and performing a pickup maneuver.

    This function builds a task graph consisting of:
    1. A node to navigate to a specific zone.
    2. A node to execute a forward maneuver to pick up items.
    The nodes are connected with a direct transition.

    Args:
        zone_pickup_id (int): The identifier for the pickup zone.

    Returns:
        BaseSubGraph: A compiled subgraph with defined entry and exit points.
    """
    pickup_sub_graph = SubGraphBuilder()

    # Add node for navigating to the specified pickup zone
    pickup_sub_graph.add_node(
        f"[Pickup] go to zone {zone_pickup_id}",
        BaseTaskNode(f"[Pickup] go to zone {zone_pickup_id}", GoToStuffZoneToPickUp(0)),
    )

    # Add node for precise forward motion to perform pickup
    pickup_sub_graph.add_node(
        f"[Pickup] go to take stuff {zone_pickup_id}",
        BaseTaskNode(f"[Pickup] go to take stuff {zone_pickup_id}", PreciseForward(10)),
    )

    # Connect the navigation node to the pickup maneuver node
    pickup_sub_graph.connect(
        f"[Pickup] go to zone {zone_pickup_id}",
        DirectTransition(
            pickup_sub_graph.nodes[f"[Pickup] go to take stuff {zone_pickup_id}"]
        ),
    )

    return pickup_sub_graph.build(
        entry=f"[Pickup] go to zone {zone_pickup_id}",
        exits=f"[Pickup] go to take stuff {zone_pickup_id}",
    )
