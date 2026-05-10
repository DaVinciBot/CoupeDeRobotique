"""Actuator tasks for winter game."""

from __future__ import annotations

from typing import TYPE_CHECKING, override

from strategy.core.tasks import BaseTask

if TYPE_CHECKING:
    from boombot_strategy.winter_game_context import WinterGameContext


class BaseActuatorTask(BaseTask["WinterGameContext"]):
    """Base class for actuator tasks that update the score."""

    def _add_points(self, ctx: WinterGameContext) -> None:
        points = self.points
        ctx.point += points(ctx) if callable(points) else points


class ExtendCursor(BaseActuatorTask):
    """Extend the cursor actuator."""

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=1.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.extend_cursor()
        self._add_points(ctx)
        return True


class RetractCursor(BaseActuatorTask):
    """Retract the cursor actuator."""

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=1.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.retract_cursor()
        self._add_points(ctx)
        return True


class PickUpJenga(BaseActuatorTask):
    """Pick up one, several, or all Jenga pieces from a zone."""

    def __init__(
        self,
        zone_id: int | None = None,
        pins: int | list[int] | None = None,
        *,
        count: int | None = None,
        color_id: int | None = None,
    ) -> None:
        super().__init__(points=0, estimated_duration=2.0)
        self.zone_id = zone_id
        self.pins = pins
        self.count = count
        self.color_id = color_id

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.pickup(self.pins)
        if self.zone_id is not None and ctx.spatial_computation is not None:
            try:
                ctx.spatial_computation.pick_crates(
                    self.zone_id,
                    count=self.count,
                    color_id=self.color_id,
                )
            except TypeError:
                ctx.spatial_computation.pick_crates(self.zone_id)
        self._add_points(ctx)
        return True


class DepositJenga(BaseActuatorTask):
    """Deposit one, several, or all held Jenga pieces into a zone."""

    def __init__(
        self,
        zone_id: int | None = None,
        pins: int | list[int] | None = None,
        *,
        count: int | None = None,
        color_id: int | None = None,
        release_point: object | None = None,
    ) -> None:
        super().__init__(points=0, estimated_duration=2.0)
        self.zone_id = zone_id
        self.pins = pins
        self.count = count
        self.color_id = color_id
        self.release_point = release_point

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.deposit(self.pins)
        if ctx.spatial_computation is not None and self.zone_id is None:
            release_crates = getattr(ctx.spatial_computation, "release_crates", None)
            if release_crates is not None:
                release_crates(
                    count=self.count,
                    color_id=self.color_id,
                    point=self.release_point,
                )
        elif self.zone_id is not None and ctx.spatial_computation is not None:
            try:
                ctx.spatial_computation.drop_crates(
                    self.zone_id,
                    count=self.count,
                    color_id=self.color_id,
                )
            except TypeError:
                ctx.spatial_computation.drop_crates(self.zone_id)
        self._add_points(ctx)
        return True


class ExtendArm(BaseActuatorTask):
    """Extend the arm servos."""

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=1.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.extend_arm()
        self._add_points(ctx)
        return True


class RetractArm(BaseActuatorTask):
    """Retract the arm servos."""

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=1.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.retract_arm()
        self._add_points(ctx)
        return True


class PrepareRotation(ExtendArm):
    """Compatibility task: there is no rotation anymore, only arm extension."""


class RotateJenga(BaseActuatorTask):
    """Compatibility task: no-op because Jengas no longer change color."""

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=0.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        self._add_points(ctx)
        return True


class BlockJenga(PickUpJenga):
    """Compatibility task for older pickup graphs."""


class SafeRetractAll(DepositJenga):
    """Compatibility task for older deposit graphs."""


class DeployCursor(ExtendCursor):
    """Compatibility task for older cursor graphs."""
