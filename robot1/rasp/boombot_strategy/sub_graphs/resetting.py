"""Subgraph for retrieving elements located on the arena wall."""

from __future__ import annotations
from math import pi


from boombot_strategy.tasks.navigation_tasks import (
    GoToClosestFreeWall,
    RelativeForward,
)

from geometry import OrientedPoint
from boombot_strategy.show_game_context import ShowGameContext
from boombot_strategy.tasks.navigation_tasks.odometrie import SetOdometrie
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition


def get_resetting_subgraph(ctx: ShowGameContext) -> BaseSubGraph:
    """
    Build a recalage subgraph to reposition the robot against the wall.
    Returns:
        BaseSubGraph:
            Subgraph representing the recalage sequence.
    """
    subgraph = SubGraphBuilder()
    goal = ctx.arena.get_closest_wall_goal()

    # Node: Navigate to the wall
    node_go_wall = "[Resetting] Go to closest free wall"
    subgraph.add_node(
        node_go_wall,
        BaseTaskNode(name=node_go_wall, tasks=GoToClosestFreeWall(goal)),
    )
    # Node: Force contact with the wall
    node_forward = "[Resetting] Move forward to reset position"
    subgraph.add_node(
        node_forward,
        BaseTaskNode(name=node_forward, tasks=RelativeForward(8)),  # 8 arbitraire sa mère à tester
    )

    node_reset_odometry = "[Resetting] Reset odometry after recalage"
    subgraph.add_node(
        node_reset_odometry,
        BaseTaskNode(
            name=node_reset_odometry,
            tasks=SetOdometrie(goal.x, goal.y, goal.theta),
        ),
    )

    # Define transitions between nodes
    subgraph.connect(node_go_wall, DirectTransition(subgraph.nodes[node_forward]))
    subgraph.connect(node_forward, DirectTransition(subgraph.nodes[node_reset_odometry]))

    # Return the finalized subgraph with defined entry and exit nodes
    return subgraph.build(
        entry=node_go_wall,
        exits=node_reset_odometry,
    )
