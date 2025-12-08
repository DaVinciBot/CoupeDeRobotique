"""Subgraph for retrieving elements located on the arena wall."""

from __future__ import annotations

from typing import TYPE_CHECKING

from boombot_strategy.tasks.navigation_tasks import (
    GoToClosestFreeWall,
    RelativeBackward,
)
from boombot_strategy.tasks.navigation_tasks.odometrie import WallSetOdometrie
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition

if TYPE_CHECKING:
    from geometry.oriented_point import OrientedPoint
    from strategy.core.base_game_context import BaseGameContext


def get_resetting_subgraph() -> BaseSubGraph:
    """Build a recalage subgraph to reposition the robot against the wall.

    Returns:
        BaseSubGraph:
            Subgraph representing the recalage sequence.
    """
    subgraph = SubGraphBuilder()

    # Node: Navigate to the wall
    def goal(ctx: BaseGameContext) -> OrientedPoint | None:
        return ctx.arena.get_closest_wall_goal()

    node_go_wall = "[Resetting] Go to closest free wall"
    subgraph.add_node(
        node_go_wall,
        BaseTaskNode(name=node_go_wall, tasks=GoToClosestFreeWall(goal)),
    )

    # Node: Force contact with the wall
    node_forward = "[Resetting] Move forward to reset position"
    subgraph.add_node(
        node_forward,
        BaseTaskNode(
            name=node_forward,
            tasks=RelativeBackward(8),  # FIXME: déterminer valeur
        ),
    )

    # Node: Reset odometry after resetting
    node_reset_odometry = "[Resetting] Reset odometry after resetting"
    subgraph.add_node(
        node_reset_odometry,
        BaseTaskNode(
            name=node_reset_odometry,
            tasks=WallSetOdometrie(),
        ),
    )

    # Define transitions between nodes
    subgraph.connect(node_go_wall, DirectTransition(subgraph.nodes[node_forward]))
    subgraph.connect(
        node_forward,
        DirectTransition(subgraph.nodes[node_reset_odometry]),
    )

    # Return the finalized subgraph with defined entry and exit nodes
    return subgraph.build(
        entry=node_go_wall,
        exits=node_reset_odometry,
    )
