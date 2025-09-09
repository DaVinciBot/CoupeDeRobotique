"""Subgraph to handle construction sequences within a zone."""

from __future__ import annotations

import time

from boombot_strategy.tasks.actuator_task import Build, Deposit, PickUp
from boombot_strategy.tasks.navigation_tasks import RelativeBackward, RelativeForward
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToConstruct,
)
from strategy.core import BaseSubGraph, BaseTaskNode, DirectTransition, SubGraphBuilder


def get_construct_subgraph(zone_id: int, back_offset: int = 0) -> BaseSubGraph:
    """Create a construction subgraph for a specific zone.

    The subgraph includes navigation to the zone, positioning forward,
    item placement using actuators, and a backward maneuver for alignment or
    disengagement.

    Args:
        zone_id (int): Identifier for the target construction zone.
        back_offset (int, optional):
            Distance already covered behind the zone, used to adjust forward motion.
            Defaults to 0.

    Returns:
        BaseSubGraph: A compiled subgraph that defines the sequence of
            construction-related tasks.

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

    node_pickup = f"[Construct] Pickup at zone {zone_id}"
    subgraph.add_node(
        node_pickup,
        BaseTaskNode(
            name=node_pickup,
            tasks=PickUp(),
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
    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_pickup]))
    subgraph.connect(node_pickup, DirectTransition(subgraph.nodes[node_prepare]))
    subgraph.connect(node_prepare, DirectTransition(subgraph.nodes[node_place]))
    subgraph.connect(node_place, DirectTransition(subgraph.nodes[node_back]))

    # Return compiled subgraph with defined entry and exit
    return subgraph.build(
        entry=node_navigate,
        exits=node_back,
    )


def get_construct_one_floor_subgraph(
    zone_id: int,
    back_offset: int = 0,
) -> BaseSubGraph:
    """Create a one-floor construction subgraph for a given zone.

    The subgraph includes navigation to the zone, positioning forward,
    item placement using actuators, and a backward maneuver for alignment or
    disengagement.

    Args:
        zone_id (int): Identifier for the target construction zone.
        back_offset (int, optional):
            Distance already covered behind the zone, used to adjust forward motion.
            Defaults to 0.

    Returns:
        BaseSubGraph: A compiled subgraph that defines the sequence of
            construction-related tasks.

    """
    subgraph = SubGraphBuilder()

    # Node: Navigate to construction zone
    node_navigate = f"[Construct_One_Floor] Navigate to zone {zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToColorReservedZoneToConstruct(zone_id),
        ),
    )
    time.sleep(10)
    # Node: Move forward to prepare for placement
    node_prepare = f"[Construct_One_Floor] Position at zone {zone_id}"
    subgraph.add_node(
        node_prepare,
        BaseTaskNode(
            name=node_prepare,
            tasks=RelativeForward(18 - back_offset),
        ),
    )

    # Node: Place item with actuators
    node_place = f"[Construct_One_Floor] Place item at zone {zone_id}"
    subgraph.add_node(
        node_place,
        BaseTaskNode(name=node_place, tasks=Deposit()),
    )

    # Node: Perform backward maneuver after placement
    node_back = f"[Construct_One_Floor] Backward from zone {zone_id}"
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
