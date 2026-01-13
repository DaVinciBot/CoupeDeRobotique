"""Actuator-related task implementations for the Boombot strategy."""

from __future__ import annotations

import time
from typing import override

from a_config_loader import CONFIG
from boombot_strategy.winter_game_context import WinterGameContext
from strategy.core.tasks import BaseTask


class ReadyToApproachToPickUp(BaseTask[WinterGameContext]):
    """Activate the actuator's approach mechanism to prepare for pickup."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to get ready to approach and pick up an object.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.ready_to_approach_to_pickup()
        ctx.point += self.points()
        return True


class PrepareToPickUp(BaseTask[WinterGameContext]):
    """Task to prepare the actuator for picking up an object."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to prepare for a pickup, then wait briefly.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.ready_to_pickup()
        ctx.point += self.points()
        time.sleep(1)
        return True


class PickUp(BaseTask[WinterGameContext]):
    """Task to perform the pickup action using the actuator."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to pick up an object, then wait briefly.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.pick_up()
        ctx.point += self.points()
        time.sleep(1)
        return True


class Build(BaseTask[WinterGameContext]):
    """Task to execute a build operation and update the game score accordingly."""

    @override
    def points(self) -> int:
        """Return the points awarded for completing this task.

        Returns:
            int: The number of points for this task.
        """
        return CONFIG.BUILD_TWO_FLOORS

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator build command and increment the score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.build_floors()
        ctx.point += self.points()
        time.sleep(1)
        return True


class Deposit(BaseTask[WinterGameContext]):
    """Release carried items and update score."""

    @override
    def points(self) -> int:
        """Return the points awarded for completing this task.

        Returns:
            int: The number of points for this task.
        """
        return CONFIG.BUILD_ONE_FLOOR

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Demagnetize all actuators and update score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.demagnetize_all()
        ctx.point += self.points()
        time.sleep(1)
        return True


class BlockBanner(BaseTask[WinterGameContext]):
    """Task to activate the banner-blocking actuator."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to block the banner.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.block_banner()
        ctx.point += self.points()
        return True


class DeplacementPosition(BaseTask[WinterGameContext]):
    """Task to adjust the actuator to a predefined displacement position."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to move to a displacement position.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.deplacement_position()
        ctx.point += self.points()
        return True


class DeplacementObject(BaseTask[WinterGameContext]):
    """Task to adjust the actuator to a predefined displacement position."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator command to move to a displacement position.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action.
        """
        ctx.actuators.deplacement_object()
        ctx.point += self.points()
        return True
