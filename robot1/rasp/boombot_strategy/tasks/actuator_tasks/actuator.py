"""Actuator tasks for winter game."""
from __future__ import annotations

import time
from typing import override

from boombot_strategy.winter_game_context import WinterGameContext
from strategy.core.tasks import BaseTask


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
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class SafeRetractAll(BaseTask[WinterGameContext]):

    def __init__(self) -> None:
        super().__init__(points=0, estimated_duration=2.0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        ctx.actuators.retract_all()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(0.5)
        return True
