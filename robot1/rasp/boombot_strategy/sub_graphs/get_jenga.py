from __future__ import annotations

from boombot_strategy.winter_game_context import WinterGameContext
from boombot_strategy.tasks.navigation_tasks import GoToStuffZoneToPickUp
from boombot_strategy.tasks.navigation_tasks import RelativeForward, RelativeBackward
from boombot_strategy.tasks.actuator_tasks import (
    BlockJenga,
)

from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition


def get_pickup_jenga_subgraph(zone_id: int, ctx: WinterGameContext) -> BaseSubGraph:
    subgraph = SubGraphBuilder()

    node_navigate = f"[Pickup Jenga] Navigate to zone {zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToStuffZoneToPickUp(zone_id, ctx),
        ),
    )

    node_align = f"[Pickup Jenga] Align at zone {zone_id}"
    subgraph.add_node(
        node_align,
        BaseTaskNode(
            name=node_align,
            tasks=RelativeForward(5),
        ),
    )

    node_block = f"[Pickup Jenga] Block Jenga {zone_id}"
    subgraph.add_node(
        node_block,
        BaseTaskNode(
            name=node_block,
            tasks=BlockJenga(),
        ),
    )

    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_align]))
    subgraph.connect(node_align, DirectTransition(subgraph.nodes[node_block]))

    return subgraph.build(
        entry=node_navigate,
        exits=node_block,
    )
