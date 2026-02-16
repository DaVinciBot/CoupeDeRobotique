from __future__ import annotations

from geometry import OrientedPoint

from boombot_strategy.tasks.navigation_tasks import RelativeForward, RelativeBackward
from boombot_strategy.tasks.actuator_task import DeployCursor
from boombot_strategy.tasks.navigation_tasks.go_to_cursor_start import (
    GoToCursorStart,
)

from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition


def get_cursor_alignment_forward_subgraph(
    target_pose: OrientedPoint,
    forward_distance: float = 20,
) -> BaseSubGraph:

    subgraph = SubGraphBuilder()

    node_navigate = "[Cursor] Go to start"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToCursorStart(target_pose),
        ),
    )

    node_deploy = "[Cursor] Deploy"
    subgraph.add_node(
        node_deploy,
        BaseTaskNode(
            name=node_deploy,
            tasks=DeployCursor(),
        ),
    )

    node_forward = "[Cursor] Fine forward alignment"
    subgraph.add_node(
        node_forward,
        BaseTaskNode(
            name=node_forward,
            tasks=RelativeForward(forward_distance),
        ),
    )

    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_deploy]))
    subgraph.connect(node_deploy, DirectTransition(subgraph.nodes[node_forward]))

    return subgraph.build(
        entry=node_deploy,
        exits=node_forward,
    )


def get_cursor_alignment_backward_subgraph(
        target_pose: OrientedPoint,
        backward_distance: float = 20,
) -> BaseSubGraph:
    subgraph = SubGraphBuilder()

    node_navigate = "[Cursor] Go to start"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToCursorStart(target_pose),
        ),
    )

    node_deploy = "[Cursor] Deploy"
    subgraph.add_node(
        node_deploy,
        BaseTaskNode(
            name=node_deploy,
            tasks=DeployCursor(),
        ),
    )

    node_backward = "[Cursor] Fine forward alignment"
    subgraph.add_node(
        node_backward,
        BaseTaskNode(
            name=node_backward,
            tasks=RelativeForward(backward_distance),
        ),
    )

    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_deploy]))
    subgraph.connect(node_deploy, DirectTransition(subgraph.nodes[node_backward]))

    return subgraph.build(
        entry=node_deploy,
        exits=node_backward,
    )
