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
        print("ActuatorTask: Executing pickup action.")
        ctx.spatial_computation.pick_crates(zone_id=3)  # C'est pour l'exemple mais la on donne le zone id en parametre
        time.sleep(1)
        return True


class Build(BaseTask[WinterGameContext]):
    """Task to execute a build operation and update the game score accordingly."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Execute the actuator build command and increment the score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.build_floors()
        ctx.score += CONFIG.BUILD_TWO_FLOORS
        ctx.spatial_computation.reverse_crate()
        time.sleep(1)
        return True


class Deposit(BaseTask[WinterGameContext]):
    """Release carried items and update score."""

    @override
    def handle(self, ctx: WinterGameContext) -> bool:
        """Demagnetize all actuators and update score.

        Args:
            ctx (WinterGameContext): The current game context.

        Returns:
            bool: Always returns ``True`` after executing the action and delay.
        """
        ctx.actuators.demagnetize_all()
        ctx.score += CONFIG.BUILD_ONE_FLOOR
        print("ActuatorTask: Executing deposit action and updating score.")
        ctx.spatial_computation.reverse_crate()
        ctx.spatial_computation.drop_crates(zone_index=11)  # pareil c'est un exemple
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
        return True
