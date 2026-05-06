"""Actuator tasks for winter game."""

from __future__ import annotations

import time
from typing import override

from boombot_strategy.winter_game_context import WinterGameContext
from strategy.core.tasks import BaseTask


def _restrict_zone_after_deposit(ctx: WinterGameContext, zone_id: int) -> None:
    ctx.arena.restrict_zone_accessibility(zone_id)


def _make_zone_free_after_pickup(ctx: WinterGameContext, zone_id: int) -> None:
    ctx.arena.make_zone_accessible(zone_id)


class PrepareRotation(BaseTask[WinterGameContext]):
    """Task to prepare the actuator for rotation."""

    def __init__(self) -> None:
        """Initialize the PrepareRotation task."""
        super().__init__(points=0, estimated_duration=2.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to prepare for rotation, then wait briefly.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.prepare_to_rotate()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class RotateJenga(BaseTask[WinterGameContext]):
    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=3.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.rotate_jenga()
        if ctx.spatial_computation is not None:
            ctx.spatial_computation.reverse_crate()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class BlockJenga(BaseTask[WinterGameContext]):
    def __init__(self, zone_id: int | None = None) -> None:
        super().__init__(points=0, estimated_duration=2.0)
        self.zone_id = zone_id

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.block_jenga()
        if self.zone_id is not None and ctx.spatial_computation is not None:
            had_crates = bool(ctx.spatial_computation.crates.get(self.zone_id))
            ctx.spatial_computation.pick_crates(self.zone_id)
            if had_crates:
                _make_zone_free_after_pickup(ctx, self.zone_id)
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(0.5)
        return True


class SafeRetractAll(BaseTask[WinterGameContext]):
    def __init__(self, zone_id: int | None = None) -> None:
        super().__init__(points=0, estimated_duration=2.0)
        self.zone_id = zone_id

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.retract_all()
        if self.zone_id is not None and ctx.spatial_computation is not None:
            had_crates = bool(getattr(ctx.spatial_computation, "held_crates", []))
            ctx.spatial_computation.drop_crates(self.zone_id)
            if had_crates:
                _restrict_zone_after_deposit(ctx, self.zone_id)
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(0.5)
        return True


class DeployCursor(BaseTask[WinterGameContext]):
    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=1.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.deploy_cursor()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(0.5)
        return True
