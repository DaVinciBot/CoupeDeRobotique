"""Subgraph for retrieving elements located on the arena wall."""

from __future__ import annotations

from boombot_strategy.tasks.navigation_tasks import (
    GoToClosestFreeWall,
    RelativeForward,
)
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition


def get_resetting_subgraph() -> BaseSubGraph:
    """
    Build a recalage subgraph to reposition the robot against the wall.
    Returns:
        BaseSubGraph:
            Subgraph representing the recalage sequence.
    """
    subgraph = SubGraphBuilder()

    # Node: Navigate to the wall
    node_go_wall = "[Resetting] Go to closest free wall"
    subgraph.add_node(
        node_go_wall,
        BaseTaskNode(name=node_go_wall, tasks=GoToClosestFreeWall()),
    )
    # Node: Force contact with the wall
    node_forward = "[Resetting] Move forward to reset position"
    subgraph.add_node(
        node_forward,
        BaseTaskNode(name=node_forward, tasks=RelativeForward(8)),  # 8 arbitraire sa mère à tester
    )

    # Define transitions between nodes
    subgraph.connect(node_go_wall, DirectTransition(subgraph.nodes[node_forward]))

    # Return the finalized subgraph with defined entry and exit nodes
    return subgraph.build(
        entry=node_go_wall,
        exits=node_forward,
    )
