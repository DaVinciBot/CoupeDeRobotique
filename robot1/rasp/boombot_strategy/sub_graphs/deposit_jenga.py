from __future__ import annotations

from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.tasks.actuator_tasks import (
    PrepareRotation,
    RotateJenga,
    SafeRetractAll,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoToColorReservedZoneToDeposit,
    GoToDepositZone,
)
from strategy.core import BaseSubGraph, SubGraphBuilder
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition

if TYPE_CHECKING:
    from rasp.boombot_strategy.winter_game_context import WinterGameContext


def get_deposit_jenga_color_zone_subgraph(ctx: WinterGameContext) -> BaseSubGraph:
    subgraph = SubGraphBuilder()

    zone_id = CONFIG.TEAM_SPECIFIC_ZONES[ctx.arena.team_color.value]

    node_navigate = f"[Deposit_Jenga_Color] Navigate to zone {zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToColorReservedZoneToDeposit(zone_id, ctx),
        ),
    )

    node_prepare = f"[Deposit_Jenga_Color] Prepare rotation {zone_id}"
    subgraph.add_node(
        node_prepare,
        BaseTaskNode(
            name=node_prepare,
            tasks=PrepareRotation(),
        ),
    )

    node_rotate = f"[Deposit_Jenga_Color] Rotate Jengas {zone_id}"
    subgraph.add_node(
        node_rotate,
        BaseTaskNode(
            name=node_rotate,
            tasks=RotateJenga(),
        ),
    )

    node_retract = f"[Deposit_Jenga_Color] Retract {zone_id}"
    subgraph.add_node(
        node_retract,
        BaseTaskNode(
            name=node_retract,
            tasks=SafeRetractAll(),
        ),
    )

    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_prepare]))
    subgraph.connect(node_prepare, DirectTransition(subgraph.nodes[node_rotate]))
    subgraph.connect(node_rotate, DirectTransition(subgraph.nodes[node_retract]))

    return subgraph.build(
        entry=node_navigate,
        exits=node_retract,
    )


def get_deposit_jenga_deposit_zone_subgraph(
    zone_id: int, ctx: WinterGameContext
) -> BaseSubGraph:
    subgraph = SubGraphBuilder()

    node_navigate = f"[Deposit_Jenga_DepositZone] Navigate to zone {zone_id}"
    subgraph.add_node(
        node_navigate,
        BaseTaskNode(
            name=node_navigate,
            tasks=GoToDepositZone(zone_id, ctx),
        ),
    )

    node_prepare = f"[Deposit_Jenga_DepositZone] Prepare rotation {zone_id}"
    subgraph.add_node(
        node_prepare,
        BaseTaskNode(
            name=node_prepare,
            tasks=PrepareRotation(),
        ),
    )

    node_rotate = f"[Deposit_Jenga_DepositZone] Rotate Jengas {zone_id}"
    subgraph.add_node(
        node_rotate,
        BaseTaskNode(
            name=node_rotate,
            tasks=RotateJenga(),
        ),
    )

    node_retract = f"[Deposit_Jenga_DepositZone] Retract {zone_id}"
    subgraph.add_node(
        node_retract,
        BaseTaskNode(
            name=node_retract,
            tasks=SafeRetractAll(),
        ),
    )

    subgraph.connect(node_navigate, DirectTransition(subgraph.nodes[node_prepare]))
    subgraph.connect(node_prepare, DirectTransition(subgraph.nodes[node_rotate]))
    subgraph.connect(node_rotate, DirectTransition(subgraph.nodes[node_retract]))

    return subgraph.build(
        entry=node_navigate,
        exits=node_retract,
    )
