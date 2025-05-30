# ====== Code Summary ======
# This module defines a function `get_push_one_floor_to_wall_subgraph` which constructs a subgraph
# representing a series of robot actions to push a floor element to a wall in a given zone.
# The subgraph includes tasks such as preparing to approach, navigating, pushing forward,
# optionally resetting odometry, and retracting afterward. The sequence is constructed
# using task nodes and transitions within a subgraph builder.

# ====== Internal Project Imports ======
from config_loader import CONFIG
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoToStuffZoneToPickUp,
    RelativeForward,
    RelativeBackward,
    SetOdometrie,
)
from boombot_strategy.tasks.actuator_task import (
    DeplacementPosition,
    ReadyToApproachToPickUp,
)


def get_push_one_floor_to_wall_subgraph(
    zone_id: int,
    push_distance: int,
    new_x: float | None = None,
    new_y: float | None = None,
    new_theta: float | None = None,
) -> BaseSubGraph:
    """
    Construct a subgraph for pushing one floor to a wall in a specific zone.

    The task sequence includes:
      1. Getting ready to approach the target zone
      2. Navigating to the target zone
      3. Preparing actuators for push
      4. Moving forward to push
      5. Optionally resetting odometry if new coordinates are provided
      6. Retracting after the push

    Args:
        zone_id (int): The ID of the target zone.
        push_distance (int): The distance to push forward in millimeters.
        new_x (float | None): Optional new X-coordinate for odometry reset.
        new_y (float | None): Optional new Y-coordinate for odometry reset.
        new_theta (float | None): Optional new orientation (theta) for odometry reset.

    Returns:
        BaseSubGraph: The constructed subgraph representing the task sequence.
    """
    odometrie_to_reset: bool = any(v is not None for v in (new_x, new_y, new_theta))
    builder = SubGraphBuilder()

    # 1) Ready to approach the zone
    node_ready = f"[Push][Zone{zone_id}] DeplacementPosition"
    builder.add_node(
        node_ready,
        BaseTaskNode(name=node_ready, tasks=DeplacementPosition()),
    )

    # 2) Navigate to the target zone
    node_navigate = f"[Push][Zone{zone_id}] NavigateToZone"
    builder.add_node(
        node_navigate,
        BaseTaskNode(name=node_navigate, tasks=GoToStuffZoneToPickUp(zone_id)),
    )

    # 3) Prepare actuator for pushing
    node_prepare = f"[Push][Zone{zone_id}] PrepareForPush"
    builder.add_node(
        node_prepare,
        BaseTaskNode(name=node_prepare, tasks=ReadyToApproachToPickUp()),
    )

    # 4) Execute forward push
    node_push = f"[Push][Zone{zone_id}] PushForward_{push_distance}mm"
    builder.add_node(
        node_push,
        BaseTaskNode(name=node_push, tasks=RelativeForward(push_distance)),
    )

    # 5) Optional odometry reset
    if odometrie_to_reset:
        node_reset = f"[Push][Zone{zone_id}] ResetOdometry"
        builder.add_node(
            node_reset,
            BaseTaskNode(
                name=node_reset,
                tasks=SetOdometrie(new_x, new_y, new_theta),
            ),
        )

    # 6) Retract after push
    node_retract = f"[Push][Zone{zone_id}] RetractAfterPush"
    builder.add_node(
        node_retract,
        BaseTaskNode(name=node_retract, tasks=RelativeBackward(50)),
    )

    # Define transitions between tasks
    builder.connect(node_ready, DirectTransition(builder.nodes[node_navigate]))
    builder.connect(node_navigate, DirectTransition(builder.nodes[node_prepare]))
    builder.connect(node_prepare, DirectTransition(builder.nodes[node_push]))

    if odometrie_to_reset:
        builder.connect(node_push, DirectTransition(builder.nodes[node_reset]))
        builder.connect(node_reset, DirectTransition(builder.nodes[node_retract]))
    else:
        builder.connect(node_push, DirectTransition(builder.nodes[node_retract]))

    # Build and return the final subgraph
    return builder.build(
        entry=node_ready,
        exits=node_retract,
    )
