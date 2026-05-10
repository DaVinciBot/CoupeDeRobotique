"""Non-linear jenga pick and deposit strategy."""

from __future__ import annotations

import copy
import time
from math import pi
from typing import TYPE_CHECKING

from a_config_loader import CONFIG
from boombot_strategy.strategies.base_strategy import BaseStrategy
from boombot_strategy.tasks.actuator_tasks import (
    BlockJenga,
    DeployCursor,
    PrepareRotation,
    RotateJenga,
    SafeRetractAll,
)
from boombot_strategy.tasks.navigation_tasks import (
    GoToDepositZone,
    GoToStuffZoneToPickUp,
    RelativeBackward,
    RelativeForward,
)
from boombot_strategy.tasks.navigation_tasks.go_to_color_reserved_zone import (
    GoToColorReservedZoneToFinishGame,
)
from boombot_strategy.tasks.navigation_tasks.go_to_cursor_start import GoToCursorStart
from geometry import OrientedPoint
from log_manager import LogLogger
from navigation.path_planner.astar_path_planner import (
    AStarPathPlanner,
    AStarPathPlannerParams,
    AStarPathPlannerPlanPathParams,
)
from navigation.path_planner.structs import Direction
from strategy.core import GraphRunner
from strategy.core.task_nodes import BaseTaskNode
from strategy.core.task_nodes.scoring_functions import ConstantScoringFunction
from strategy.core.transitions import DirectTransition
from strategy.core.transitions.conditional_transition import (
    ConditionalTransition,
    FromFunctionTransitionCondition,
)

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext

ACTION_DEADLINE_SECONDS = 85.0
RETURN_TO_BASE_SECONDS = 75.0


def _can_start_action(start_time: float) -> bool:
    return time.time() - start_time < RETURN_TO_BASE_SECONDS


def _pickup_zone_has_crates(ctx: WinterGameContext, zone_id: int) -> bool:
    spatial_computation = getattr(ctx, "spatial_computation", None)
    if spatial_computation is None:
        return True

    return bool(spatial_computation.crates.get(zone_id))


def _zone_is_reachable(ctx: WinterGameContext, zone_id: int) -> bool:
    goal = ctx.arena.compute_goal_position(zone_id)
    if goal is None:
        return False

    current_position = ctx.rolling_basis.odometrie
    path_planner = AStarPathPlanner(
        AStarPathPlannerParams(
            grid=copy.deepcopy(ctx.arena.grid_manager.get_static_and_dynamic_grid()),
            path_resolution=5,
            chunk_size=CONFIG.ARENA_CHUNK_SIZE,
            start=current_position,
            goal=goal,
            direction=Direction.FORWARD,
        ),
    )
    return bool(
        path_planner.plan_path(
            AStarPathPlannerPlanPathParams(
                start=current_position,
                goal=goal,
            ),
        ),
    )


def _robot_has_crates(ctx: WinterGameContext) -> bool:
    spatial_computation = getattr(ctx, "spatial_computation", None)
    if spatial_computation is None:
        return True

    return bool(getattr(spatial_computation, "held_crates", []))


def _deposit_zone_can_receive_crates(ctx: WinterGameContext, zone_id: int) -> bool:
    spatial_computation = getattr(ctx, "spatial_computation", None)
    if spatial_computation is not None and spatial_computation.crates.get(zone_id):
        return False

    zone = ctx.arena.get_zone_by_location(zone_id)
    if zone is None:
        return False

    return zone.is_accessible() and _zone_is_reachable(ctx, zone_id)


def _when_robot_has_crates(target: BaseTaskNode) -> ConditionalTransition:
    return ConditionalTransition(
        target,
        FromFunctionTransitionCondition(
            lambda _from_node, _next_node, ctx: _robot_has_crates(ctx),
        ),
    )


def _when_robot_has_crates_and_deposit_zone_is_free(
    target: BaseTaskNode,
    zone_id: int,
    start_time: float,
) -> ConditionalTransition:
    return ConditionalTransition(
        target,
        FromFunctionTransitionCondition(
            lambda _from_node, _next_node, ctx: _can_start_action(start_time)
            and _robot_has_crates(ctx)
            and _deposit_zone_can_receive_crates(ctx, zone_id),
        ),
    )


def _when_pickup_zone_has_crates(
    target: BaseTaskNode,
    zone_id: int,
    start_time: float,
) -> ConditionalTransition:
    return ConditionalTransition(
        target,
        FromFunctionTransitionCondition(
            lambda _from_node, _next_node, ctx: _can_start_action(start_time)
            and _pickup_zone_has_crates(ctx, zone_id)
            and _zone_is_reachable(ctx, zone_id),
        ),
    )


class SmartZoneStrategy(BaseStrategy):
    def __init__(self, ctx: WinterGameContext) -> None:
        super().__init__(ctx)
        self.start_time = time.time()
        self.pickup_zones_list = CONFIG.PICKUP_ZONES_LIST
        self.deposit_zones_list = CONFIG.DEPOSIT_ZONES_LIST

        if ctx.arena.team_color.name.lower() == "yellow":
            goal = OrientedPoint(20, 10, 0)
            cursor_tasks = [
                GoToCursorStart(goal, ctx),
                DeployCursor(),
                RelativeBackward(20),
            ]
        else:
            goal = OrientedPoint(280, 10, pi)
            cursor_tasks = [
                GoToCursorStart(goal, ctx),
                DeployCursor(),
                RelativeForward(20),
            ]

        cursor_node = BaseTaskNode(
            name="[Cursor] Align",
            tasks=cursor_tasks,
            repeatable=False,
            max_visits=1,
        )

        pickup_nodes: list[BaseTaskNode] = [
            BaseTaskNode(
                name=f"[Pickup Jenga] Zone {zone_id}",
                tasks=[
                    GoToStuffZoneToPickUp(zone_id, ctx),
                    RelativeForward(5),
                    BlockJenga(zone_id),
                ],
                repeatable=True,
                max_visits=None,
            )
            for zone_id in self.pickup_zones_list
        ]

        deposit_nodes: list[BaseTaskNode] = [
            BaseTaskNode(
                name=f"[Deposit Jenga] Zone {zone_id}",
                tasks=[
                    GoToDepositZone(zone_id, ctx),
                    PrepareRotation(),
                    RotateJenga(),
                    SafeRetractAll(zone_id),
                ],
                repeatable=True,
                max_visits=None,
            )
            for zone_id in self.deposit_zones_list
        ]

        go_to_backstage = BaseTaskNode(
            name="[End] Go to backstage",
            tasks=GoToColorReservedZoneToFinishGame(self.zones["backstage_zone"], ctx),
            scoring_function=ConstantScoringFunction(score=-1e9),
            repeatable=False,
            max_visits=1,
        )

        for pickup_node in pickup_nodes:
            for zone_id, deposit_node in zip(
                self.deposit_zones_list,
                deposit_nodes,
                strict=False,
            ):
                pickup_node.add_transition(
                    _when_robot_has_crates_and_deposit_zone_is_free(
                        deposit_node,
                        zone_id,
                        self.start_time,
                    )
                )
            pickup_node.add_transition(DirectTransition(go_to_backstage))

        for deposit_node in deposit_nodes:
            for zone_id, pickup_node in zip(
                self.pickup_zones_list,
                pickup_nodes,
                strict=False,
            ):
                deposit_node.add_transition(
                    _when_pickup_zone_has_crates(
                        pickup_node,
                        zone_id,
                        self.start_time,
                    )
                )
            deposit_node.add_transition(DirectTransition(go_to_backstage))

        for zone_id, pickup_node in zip(
            self.pickup_zones_list,
            pickup_nodes,
            strict=False,
        ):
            cursor_node.add_transition(
                _when_pickup_zone_has_crates(
                    pickup_node,
                    zone_id,
                    self.start_time,
                )
            )
        cursor_node.add_transition(DirectTransition(go_to_backstage))

        self.runner = GraphRunner(
            logger=LogLogger(
                identifier="SmartZoneStrategyRunner",
                follow_logger_manager_rules=True,
            ),
            start=cursor_node,
        )
