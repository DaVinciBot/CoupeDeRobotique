"""Actuator-related task implementations for the Boombot strategy."""

from __future__ import annotations

import time
from typing import override

from a_config_loader import CONFIG
from boombot_strategy.winter_game_context import WinterGameContext
from strategy.core.tasks import BaseTask


class ReadyToApproachToPickUp(BaseTask[WinterGameContext]):
    """Activate the actuator's approach mechanism to prepare for pickup."""

    def __init__(self) -> None:
        """Initialize the ReadyToApproachToPickUp task."""
        super().__init__(estimated_duration=2.5, points=0)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to get ready to approach and pick up an object.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.ready_to_approach_to_pickup()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class PrepareToPickUp(BaseTask[WinterGameContext]):
    """Task to prepare the actuator for picking up an object."""

    def __init__(self) -> None:
        """Initialize the PrepareToPickUp task."""
        super().__init__(points=0, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to prepare for a pickup, then wait briefly.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.ready_to_pickup()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(1)
        return True


class PickUp(BaseTask[WinterGameContext]):
    """Task to perform the pickup action using the actuator."""

    def __init__(self) -> None:
        """Initialize the PickUp task."""
        super().__init__(points=0, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to pick up an object, then wait briefly.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.pick_up()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(1)
        return True


class Build(BaseTask[WinterGameContext]):
    """Task to execute a build operation and update the game score accordingly."""

    def __init__(self) -> None:
        """Initialize the Build task."""
        super().__init__(points=CONFIG.BUILD_TWO_FLOORS, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator build command and increment the score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.build_floors()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(1)
        return True


class Deposit(BaseTask[WinterGameContext]):
    """Release carried items and update score."""

    def __init__(self) -> None:
        """Initialize the Deposit task."""
        super().__init__(points=CONFIG.BUILD_ONE_FLOOR, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Demagnetize all actuators and update score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.demagnetize_all()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        time.sleep(1)
        return True


class BlockBanner(BaseTask[WinterGameContext]):
    """Task to activate the banner-blocking actuator."""

    def __init__(self) -> None:
        """Initialize the BlockBanner task."""
        super().__init__(points=0, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to block the banner.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.block_banner()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class DeplacementPosition(BaseTask[WinterGameContext]):
    """Task to adjust the actuator to a predefined displacement position."""

    def __init__(self) -> None:
        """Initialize the DeplacementPosition task."""
        super().__init__(points=0, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to move to a displacement position.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.deplacement_position()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True


class DeplacementObject(BaseTask[WinterGameContext]):
    """Task to adjust the actuator to a predefined displacement position."""

    def __init__(self) -> None:
        """Initialize the DeplacementObject task."""
        super().__init__(points=0, estimated_duration=2.5)

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to move to a displacement position.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.deplacement_object()
        p = self.points
        ctx.point += p(ctx) if callable(p) else p
        return True
