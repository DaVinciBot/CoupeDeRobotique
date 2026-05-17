"""Subgraph for handling banner deployment actions."""

from __future__ import annotations

import math

from botladyyy_strategy.tasks.actuator_task import BlockBanner, DeplacementPosition
from botladyyy_strategy.tasks.navigation_tasks import (
    RelativeBackward,
    RelativeForward,
    SetOdometrie,
)
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition


def get_banner_deployment_subgraph() -> BaseSubGraph:
    """Construct a subgraph for executing the banner deployment sequence.

    The steps include:
      1. Locking the banner mechanism to prepare for deployment.
      2. Moving forward to the deployment point.
      3. Releasing the mechanism to deploy the banner.
      4. Resetting the robot's orientation using odometry.
      5. Retracting slightly after deployment.
      6. Moving to a specific post-deployment position.

    Returns:
        BaseSubGraph: A structured subgraph representing the deployment sequence.
    """
    builder = SubGraphBuilder()

    # 1) Lock banner mechanism
    node_lock = "[Banner][Deploy] LockMechanism"
    builder.add_node(
        node_lock,
        BaseTaskNode(name=node_lock, tasks=BlockBanner()),
    )

    # 2) Advance to deploy position
    node_advance = "[Banner][Deploy] AdvanceToDeployPoint"
    builder.add_node(
        node_advance,
        BaseTaskNode(name=node_advance, tasks=RelativeForward(7)),
    )

    # 3) Reset odometry orientation
    node_reset = "[Banner][Deploy] ResetOdometry"
    builder.add_node(
        node_reset,
        BaseTaskNode(
            name=node_reset,
            tasks=SetOdometrie(theta=-math.pi / 2),
        ),
    )

    # 4) Release banner mechanism
    node_release = "[Banner][Deploy] ReleaseMechanism"
    builder.add_node(
        node_release,
        BaseTaskNode(name=node_release, tasks=DeplacementPosition()),
    )

    # 5) Retract after deployment
    node_retract = "[Banner][Deploy] RetractAfterDeploy"
    builder.add_node(
        node_retract,
        BaseTaskNode(name=node_retract, tasks=RelativeBackward(20)),
    )

    # Define task transitions in order
    builder.connect(node_lock, DirectTransition(builder.nodes[node_advance]))
    builder.connect(node_advance, DirectTransition(builder.nodes[node_release]))
    builder.connect(node_release, DirectTransition(builder.nodes[node_reset]))
    builder.connect(node_reset, DirectTransition(builder.nodes[node_retract]))

    # Build and return the subgraph
    return builder.build(
        entry=node_lock,
        exits=node_retract,
    )
