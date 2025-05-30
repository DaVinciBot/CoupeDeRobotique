# ====== Code Summary ======
# This module defines a function `get_banner_deployement_subgraph` that constructs a task subgraph
# for deploying a banner using a sequence of actuator and movement tasks.
# The sequence includes blocking the banner, moving forward to deploy, unblocking for extraction,
# and a final backward motion to safely disengage. All steps are connected via direct transitions
# and returned as a `BaseSubGraph` for strategic execution.

# ====== Local Project Imports ======
from strategy.core import (
    SubGraphBuilder,
    BaseTaskNode,
    DirectTransition,
    BaseSubGraph,
)

# ====== Internal Project Imports ======
from config_loader import CONFIG
from boombot_strategy.tasks.navigation_tasks import RelativeForward, RelativeBackward
from boombot_strategy.tasks.actuator_task import BlockBanner, ReadyToApproachToPickUp, DeplacementPosition


def get_banner_deployment_subgraph() -> BaseSubGraph:
    """
    Build a subgraph that defines the sequence of tasks for deploying a banner.

    The subgraph includes blocking the banner mechanism, moving forward to deploy it,
    unblocking for further tasks, and a backward maneuver to extract safely.

    Returns:
        BaseSubGraph: A compiled subgraph representing the banner deployment operation.
    """
    subgraph = SubGraphBuilder()

    # Node: Block the banner to prepare for deployment
    node_block_banner = "[Banner Deployment] Block banner"
    subgraph.add_node(
        node_block_banner,
        BaseTaskNode(
            name=node_block_banner,
            tasks=BlockBanner(),
        ),
    )

    # Node: Move forward to reach banner deployment position
    node_forward_to_deploy_banner = "[Banner Deployment] Move forward to deploy banner"
    subgraph.add_node(
        node_forward_to_deploy_banner,
        BaseTaskNode(
            name=node_forward_to_deploy_banner,
            tasks=RelativeForward(7),
        ),
    )

    # Node: Unblock banner (releasing mechanism or resetting state)
    node_unblock_banner = "[Banner Deployment] Unblock banner"
    subgraph.add_node(
        node_unblock_banner,
        BaseTaskNode(
            name=node_unblock_banner,
            tasks=ReadyToApproachToPickUp(),
        ),
    )

    # Node: Move backward to disengage after deployment
    node_backward_to_extract = "[Banner Deployment] Move backward to extract"
    subgraph.add_node(
        node_backward_to_extract,
        BaseTaskNode(
            name=node_backward_to_extract,
            tasks=RelativeBackward(20),
        ),
    )

    # Node: Deplacement position
    node_deplacement_position = "[Banner Deployment] Deplacement position"
    subgraph.add_node(
        node_deplacement_position,
        BaseTaskNode(
            name=node_deplacement_position,
            tasks=DeplacementPosition(),
        ),
    )

    # Transitions between nodes to form a linear task flow
    subgraph.connect(
        node_block_banner,
        DirectTransition(subgraph.nodes[node_forward_to_deploy_banner]),
    )
    subgraph.connect(
        node_forward_to_deploy_banner,
        DirectTransition(subgraph.nodes[node_unblock_banner]),
    )
    subgraph.connect(
        node_unblock_banner,
        DirectTransition(subgraph.nodes[node_backward_to_extract]),
    )
    subgraph.connect(
        node_backward_to_extract,
        DirectTransition(subgraph.nodes[node_deplacement_position]),
    )

    # Return the completed subgraph with specified entry and exit nodes
    return subgraph.build(
        entry=node_block_banner,
        exits=node_deplacement_position,
    )
