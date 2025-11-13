"""Subgraph for retrieving elements located on the arena wall."""

from __future__ import annotations

from boombot_strategy.tasks.navigation_tasks import (
    GoToStuffZoneToPickUp,
)
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode


def get_deplacement_subgraph(zone_id: int) -> BaseSubGraph:
    """Create a subgraph to navigate to a specified stuff zone.

    Args:
        zone_id (int): The ID of the zone to navigate to.

    Returns:
        BaseSubGraph: The constructed subgraph for navigation.
    """
    subgraph = SubGraphBuilder()
    node_navigate = f"[GoTo][Zone{zone_id}] NavigateToZone"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(name=node_navigate, tasks=GoToStuffZoneToPickUp(zone_id)),
    )

    return subgraph.build(
        entry=node_navigate,
        exits=node_navigate,
    )
