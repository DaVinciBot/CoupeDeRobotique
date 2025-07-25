# ====== Code Summary ======
# This code defines a function ``get_pickup_subgraph`` that builds a structured task graph
# for a robot to execute a pickup operation at a designated pickup zone.
# The subgraph sequentially manages navigation, preparation, approach, and the actual pickup,
# using named task nodes and transitions to ensure reliable task execution.

from boombot_strategy.tasks.actuator_task import (
    DeplacementObject,
    PrepareToPickUp,
    ReadyToApproachToPickUp,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoCentroidOfZone,
    GoToStuffZoneToPickUp,
    RelativeBackward,
)
from strategy.core import (
    BaseSubGraph,
    BaseTaskNode,
    DirectTransition,
    SubGraphBuilder,
)


def get_pickup_subgraph(pickup_zone_id: int) -> BaseSubGraph:
    """Build a subgraph that defines the sequence of tasks for picking up an object at a specified zone.

    The subgraph includes navigation to the zone, preparation steps, and execution of the pickup operation.
    Nodes are connected linearly using direct transitions to ensure an ordered task flow.

    Args:
        pickup_zone_id (int): Identifier for the pickup zone.

    Returns:
        BaseSubGraph: A subgraph representing the complete pickup operation.
    """
    subgraph = SubGraphBuilder()

    # Node: Ready to approach the pickup zone
    node_ready = f"[Pickup] Ready to approach zone {pickup_zone_id}"
    subgraph.add_node(
        node_ready,
        BaseTaskNode(name=node_ready, tasks=ReadyToApproachToPickUp()),
    )

    # Node: Navigate to the pickup zone
    node_navigate = f"[Pickup] Navigate to zone {pickup_zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(name=node_navigate, tasks=GoToStuffZoneToPickUp(pickup_zone_id)),
    )

    # Node: Prepare to pick up the item
    node_prepare = f"[Pickup] Prepare to pick up at zone {pickup_zone_id}"
    subgraph.add_node(
        node_prepare,
        BaseTaskNode(name=node_prepare, tasks=PrepareToPickUp()),
    )

    # Node: Move forward to the pickup point
    node_forward = f"[Pickup] Advance to pickup point at zone {pickup_zone_id}"
    subgraph.add_node(
        node_forward,
        BaseTaskNode(name=node_forward, tasks=GoCentroidOfZone(pickup_zone_id)),
    )

    # Node: Execute the pickup
    node_pickup = f"[Pickup] Pick up item at zone {pickup_zone_id}"
    subgraph.add_node(
        node_pickup,
        BaseTaskNode(name=node_pickup, tasks=DeplacementObject()),
    )

    # Node: extract from pickup zone
    node_extract = f"[Pickup] Extract from zone {pickup_zone_id}"
    subgraph.add_node(
        node_extract,
        BaseTaskNode(name=node_extract, tasks=RelativeBackward(20)),
    )

    # Define transitions between nodes
    subgraph.connect(node_ready, DirectTransition(subgraph.nodes[node_navigate]))
    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_prepare]))
    subgraph.connect(node_prepare, DirectTransition(subgraph.nodes[node_forward]))
    subgraph.connect(node_forward, DirectTransition(subgraph.nodes[node_pickup]))
    subgraph.connect(node_pickup, DirectTransition(subgraph.nodes[node_extract]))

    # Return the finalized subgraph with defined entry and exit nodes
    return subgraph.build(
        entry=node_ready,
        exits=node_extract,
    )
