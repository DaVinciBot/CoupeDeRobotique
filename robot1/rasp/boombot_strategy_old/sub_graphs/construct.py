# ====== Local Project Imports ======
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
    DefaultScoringFunction,
    ConstantScoringFunction,
    NavigationScoringFunction,
)

# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy import ShowGameContext
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToConstruct,
)
from boombot_strategy.tasks.navigation_tasks.maneuver import Backward, PreciseForward

from boombot_strategy.tasks.actuator_task.actuator_task import Build


def get_construct_sub_graph(
    zone_construct_id: int, ctx: ShowGameContext, distance_from_back_of_zone: float = 0.0
) -> BaseSubGraph:
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
            name=f"[Construct] go to zone {zone_construct_id}",
            tasks=GoToColorReservedZoneToConstruct(zone_construct_id),
            scoring_function=NavigationScoringFunction(zone_construct_id),
        ),
    )

    # Add node for preparing the construction at the specified zone
    construct_sub_graph.add_node(
        f"[Construct] prepare construction at zone {zone_construct_id}",
        BaseTaskNode(
            name=f"[Construct] prepare construction at zone {zone_construct_id}",
            tasks=PreciseForward(18 - distance_from_back_of_zone),
            scoring_function=DefaultScoringFunction(),
        ),
    )

    # Add node for actuators action of placing item
    construct_sub_graph.add_node(
        f"[Construct] placing item at zone {zone_construct_id}",
        BaseTaskNode(
            name=f"[Construct] placing item at zone {zone_construct_id}",
            tasks=Build(),
            scoring_function=ConstantScoringFunction(CONFIG.BUILD_TWO_FLOORS),
        ),
    )

    # Add node for precise backward motion to perform construction
    construct_sub_graph.add_node(
        f"[Construct] backward maneuver at zone {zone_construct_id}",
        BaseTaskNode(
            name=f"[Construct] backward maneuver at zone {zone_construct_id}",
            tasks=Backward(16),
            scoring_function=DefaultScoringFunction(),
        ),
    )

    construct_sub_graph.connect(
        f"[Construct] go to zone {zone_construct_id}",
        DirectTransition(
            construct_sub_graph.nodes[
                f"[Construct] prepare construction at zone {zone_construct_id}"
            ]
        ),
    )

    construct_sub_graph.connect(
        f"[Construct] prepare construction at zone {zone_construct_id}",
        DirectTransition(
            construct_sub_graph.nodes[
                f"[Construct] placing item at zone {zone_construct_id}"
            ]
        ),
    )

    construct_sub_graph.connect(
        f"[Construct] placing item at zone {zone_construct_id}",
        DirectTransition(
            construct_sub_graph.nodes[
                f"[Construct] backward maneuver at zone {zone_construct_id}"
            ]
        ),
    )

    return construct_sub_graph.build(
        entry=f"[Construct] go to zone {zone_construct_id}",
        exits=f"[Construct] backward maneuver at zone {zone_construct_id}",
    )
