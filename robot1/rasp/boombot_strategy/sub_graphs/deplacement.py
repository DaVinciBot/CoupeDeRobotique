"""Subgraph for retrieving elements located on the arena wall."""

from __future__ import annotations
from math import pi


from boombot_strategy.tasks.navigation_tasks import (
    GoToStuffZoneToPickUp,
)

from geometry import OrientedPoint
from boombot_strategy.show_game_context import ShowGameContext
from boombot_strategy.tasks.navigation_tasks.odometrie import SetOdometrie

from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.tasks import BaseTask
from strategy.core.transitions import DirectTransition


def get_deplacement_subgraph(zone_id: int) -> BaseSubGraph:
    subgraph = SubGraphBuilder()
    node_navigate = f"[Push][Zone{zone_id}] NavigateToZone"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(name=node_navigate, tasks=GoToStuffZoneToPickUp(zone_id)),
    )

    return subgraph.build(
        entry=node_navigate,
        exits=node_navigate,
    )
