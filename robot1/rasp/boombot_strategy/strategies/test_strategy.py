"""Test strategy for nearest winter Jenga pickup and deposit simulation."""

from __future__ import annotations

import copy
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from arena.base_arena import TeamColor
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.actuator_tasks import DepositJenga, PickUpJenga
from boombot_strategy.tasks.navigation_tasks import (
    GoToDepositZone,
    GoToOrientedPoint,
    GoToStuffZoneToPickUp,
)
from geometry import OrientedPoint, distance
from log_manager import LogLogger
from navigation.path_planner.astar_path_planner import (
    AStarPathPlanner,
    AStarPathPlannerParams,
    AStarPathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.transitions import DirectTransition

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


RELEASE_POINT = OrientedPoint(150, 100, 0)


class TestStrategy(BaseStrategy):
    """Run a nearest-zone pickup/deposit sequence for winter simulation."""

    def __init__(self, ctx: WinterGameContext) -> None:
        """Build the requested winter actuator test strategy."""
        super().__init__(ctx)

        team_color_id = 1 if ctx.arena.team_color == TeamColor.YELLOW else 0
        opponent_color_id = 0 if team_color_id == 1 else 1

        used_pickup_zones: set[int] = set()
        current_position = ctx.rolling_basis.odometrie

        first_pickup_zone = self._nearest_pickup_zone(
            ctx,
            current_position,
            used_pickup_zones,
            color_id=team_color_id,
        )
        used_pickup_zones.add(first_pickup_zone)
        current_position = ctx.arena.compute_goal_position(first_pickup_zone)

        first_deposit_zone = self._nearest_deposit_zone(ctx, current_position)
        current_position = ctx.arena.compute_goal_position(first_deposit_zone)

        second_pickup_zone = self._nearest_pickup_zone(
            ctx,
            current_position,
            used_pickup_zones,
            color_id=team_color_id,
        )
        used_pickup_zones.add(second_pickup_zone)
        current_position = ctx.arena.compute_goal_position(second_pickup_zone)

        second_deposit_zone = self._nearest_deposit_zone(ctx, current_position)
        current_position = ctx.arena.compute_goal_position(second_deposit_zone)

        mixed_pickup_zone = self._nearest_pickup_zone(
            ctx,
            current_position,
            used_pickup_zones,
            color_id=None,
        )
        used_pickup_zones.add(mixed_pickup_zone)
        current_position = ctx.arena.compute_goal_position(mixed_pickup_zone)

        final_deposit_zone = self._nearest_deposit_zone(ctx, RELEASE_POINT)

        nodes = [
            BaseTaskNode(
                name=f"[Test] Pickup 1 team Jenga from zone {first_pickup_zone}",
                tasks=[
                    GoToStuffZoneToPickUp(first_pickup_zone, ctx),
                    PickUpJenga(
                        first_pickup_zone,
                        count=1,
                        color_id=team_color_id,
                    ),
                ],
            ),
            BaseTaskNode(
                name=f"[Test] Deposit 1 team Jenga in zone {first_deposit_zone}",
                tasks=[
                    GoToDepositZone(first_deposit_zone, ctx),
                    DepositJenga(
                        first_deposit_zone,
                        count=1,
                        color_id=team_color_id,
                    ),
                ],
            ),
            BaseTaskNode(
                name=f"[Test] Pickup 2 team Jengas from zone {second_pickup_zone}",
                tasks=[
                    GoToStuffZoneToPickUp(second_pickup_zone, ctx),
                    PickUpJenga(
                        second_pickup_zone,
                        count=2,
                        color_id=team_color_id,
                    ),
                ],
            ),
            BaseTaskNode(
                name=f"[Test] Deposit 2 team Jengas in zone {second_deposit_zone}",
                tasks=[
                    GoToDepositZone(second_deposit_zone, ctx),
                    DepositJenga(
                        second_deposit_zone,
                        count=2,
                        color_id=team_color_id,
                    ),
                ],
            ),
            BaseTaskNode(
                name=f"[Test] Pickup all Jengas from zone {mixed_pickup_zone}",
                tasks=[
                    GoToStuffZoneToPickUp(mixed_pickup_zone, ctx),
                    PickUpJenga(mixed_pickup_zone),
                ],
            ),
            BaseTaskNode(
                name="[Test] Release opponent Jengas outside deposit zones",
                tasks=[
                    GoToOrientedPoint(RELEASE_POINT),
                    DepositJenga(
                        color_id=opponent_color_id,
                        release_point=RELEASE_POINT,
                    ),
                ],
            ),
            BaseTaskNode(
                name=f"[Test] Deposit remaining team Jengas in zone {final_deposit_zone}",
                tasks=[
                    GoToDepositZone(final_deposit_zone, ctx),
                    DepositJenga(final_deposit_zone, color_id=team_color_id),
                ],
            ),
        ]

        for current_node, next_node in zip(nodes, nodes[1:], strict=False):
            current_node.add_transition(DirectTransition(next_node))

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="TestStrategy",
                follow_logger_manager_rules=True,
            ),
            start=nodes[0],
        )

    @classmethod
    def _nearest_pickup_zone(
        cls,
        ctx: WinterGameContext,
        start: OrientedPoint,
        used_zone_ids: set[int],
        *,
        color_id: int | None,
    ) -> int:
        candidates = [
            zone_id
            for zone_id in CONFIG.PICKUP_ZONES_LIST
            if zone_id not in used_zone_ids
            and cls._pickup_zone_has_crates(ctx, zone_id, color_id=color_id)
            and cls._zone_is_reachable(ctx, start, zone_id)
        ]
        return cls._nearest_zone(ctx, start, candidates, "pickup")

    @classmethod
    def _nearest_deposit_zone(
        cls,
        ctx: WinterGameContext,
        start: OrientedPoint,
    ) -> int:
        candidates = [
            zone_id
            for zone_id in CONFIG.DEPOSIT_ZONES_LIST
            if cls._zone_is_reachable(ctx, start, zone_id)
        ]
        if not candidates:
            candidates = [
                zone_id
                for zone_id in CONFIG.DEPOSIT_ZONES_LIST
                if ctx.arena.compute_goal_position(zone_id) is not None
            ]
        return cls._nearest_zone(ctx, start, candidates, "deposit")

    @staticmethod
    def _pickup_zone_has_crates(
        ctx: WinterGameContext,
        zone_id: int,
        *,
        color_id: int | None,
    ) -> bool:
        spatial_computation = getattr(ctx, "spatial_computation", None)
        if spatial_computation is None:
            return True

        crates = spatial_computation.crates.get(zone_id, [])
        return any(color_id is None or crate.color_id == color_id for crate in crates)

    @staticmethod
    def _zone_is_reachable(
        ctx: WinterGameContext,
        start: OrientedPoint,
        zone_id: int,
    ) -> bool:
        goal = ctx.arena.compute_goal_position(zone_id)
        if goal is None:
            return False

        path_planner = AStarPathPlanner(
            AStarPathPlannerParams(
                grid=copy.deepcopy(ctx.arena.grid_manager.get_static_and_dynamic_grid()),
                path_resolution=5,
                chunk_size=CONFIG.ARENA_CHUNK_SIZE,
                start=start,
                goal=goal,
                direction=Direction.FORWARD,
            ),
        )
        try:
            return bool(
                path_planner.plan_path(
                    AStarPathPlannerPlanPathParams(
                        start=start,
                        goal=goal,
                    ),
                ),
            )
        except Exception:
            return False

    @staticmethod
    def _nearest_zone(
        ctx: WinterGameContext,
        start: OrientedPoint,
        zone_ids: list[int],
        kind: str,
    ) -> int:
        if not zone_ids:
            msg = f"No reachable {kind} zone found"
            raise ValueError(msg)

        return min(
            zone_ids,
            key=lambda zone_id: distance(start, ctx.arena.compute_goal_position(zone_id)),
        )
