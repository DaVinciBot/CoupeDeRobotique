# ====== Local Project Imports ======
from config_loader import CONFIG
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
    ConstantScoringFunction,
    DefaultScoringFunction,
    NavigationScoringFunction,
)

# ====== Internal Project Imports ======
from boombot_strategy import ShowGameContext
from boombot_strategy.tasks.navigation_tasks.go_to_stuff_zone import (
    GoToStuffZoneToPickUp,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import (
    PreciseForward,
)

from boombot_strategy.tasks.actuator_task.actuator_task import (
    PickUp,
    ReadyToPickUp,
)


def get_pickup_sub_graph(zone_pickup_id: int, ctx: ShowGameContext) -> BaseSubGraph:
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
        BaseTaskNode(
            name=f"[Pickup] go to zone {zone_pickup_id}",
            tasks=GoToStuffZoneToPickUp(zone_pickup_id),
            scoring_function=NavigationScoringFunction(
                ctx.arena.ally_zone.point.distance(
                    ctx.arena.compute_goal_position(zone_pickup_id)
                )
            ),
        ),
    )

    pickup_sub_graph.add_node(
        f"[Pickup] prepare pickup at zone {zone_pickup_id}",
        BaseTaskNode(
            name=f"[Pickup] prepare pickup at zone {zone_pickup_id}",
            tasks=ReadyToPickUp(),
            scoring_function=DefaultScoringFunction(),
        ),
    )

    # Add node for precise forward motion to perform pickup
    pickup_sub_graph.add_node(
        f"[Pickup] go to take stuff {zone_pickup_id}",
        BaseTaskNode(
            name=f"[Pickup] go to take stuff {zone_pickup_id}",
            tasks=PreciseForward(10),
            scoring_function=NavigationScoringFunction(
                ctx.arena.ally_zone.point.distance(
                    ctx.arena.compute_goal_position(zone_pickup_id)
                )
            ),
        ),
    )

    pickup_sub_graph.add_node(
        f"[Pickup] pickup stuff at zone {zone_pickup_id}",
        BaseTaskNode(
            name=f"[Pickup] pickup stuff at zone {zone_pickup_id}",
            tasks=PickUp(),
            scoring_function=DefaultScoringFunction(),
        ),
    )

    # Connect the navigation node to the pickup maneuver node
    pickup_sub_graph.connect(
        f"[Pickup] go to zone {zone_pickup_id}",
        DirectTransition(
            pickup_sub_graph.nodes[f"[Pickup] prepare pickup at zone {zone_pickup_id}"]
        ),
    )

    pickup_sub_graph.connect(
        f"[Pickup] prepare pickup at zone {zone_pickup_id}",
        DirectTransition(
            pickup_sub_graph.nodes[f"[Pickup] go to take stuff {zone_pickup_id}"]
        ),
    )

    pickup_sub_graph.connect(
        f"[Pickup] go to take stuff {zone_pickup_id}",
        DirectTransition(
            pickup_sub_graph.nodes[f"[Pickup] pickup stuff at zone {zone_pickup_id}"]
        ),
    )

    return pickup_sub_graph.build(
        entry=f"[Pickup] go to zone {zone_pickup_id}",
        exits=f"[Pickup] pickup stuff at zone {zone_pickup_id}",
    )
