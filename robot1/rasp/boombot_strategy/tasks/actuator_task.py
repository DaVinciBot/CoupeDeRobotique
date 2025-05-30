# ====== Code Summary ======
# This module defines several actuator control tasks for a robot, such as picking up objects,
# preparing to pick up, building structures, and adjusting position. Each task interacts with
# the actuator subsystem through the provided game context and optionally updates the score.

# ====== Standard Library Imports ======
import time

# ====== Internal Project Imports ======
from config_loader import CONFIG
from strategy.core import BaseTask
from boombot_strategy.show_game_context import ShowGameContext


class ReadyToApproachToPickUp(BaseTask):
    """
    Task to activate the actuator's approach mechanism in preparation for picking up an object.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to get ready to approach and pick up an object.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.ready_to_approach_to_pickup()
        return True


class PrepareToPickUp(BaseTask):
    """
    Task to prepare the actuator for picking up an object.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to prepare for a pickup, then wait briefly.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action and delay.
        """
        ctx.actuators.ready_to_pickup()
        time.sleep(1)
        return True


class PickUp(BaseTask):
    """
    Task to perform the pickup action using the actuator.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to pick up an object, then wait briefly.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action and delay.
        """
        ctx.actuators.pick_up()
        time.sleep(1)
        return True


class Build(BaseTask):
    """
    Task to execute a build operation and update the game score accordingly.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator build command and increment the score.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action and delay.
        """
        ctx.actuators.build_floors()
        ctx.score += CONFIG.BUILD_TWO_FLOORS
        time.sleep(1)
        return True

class Deposit(BaseTask):

    def handle(self, ctx: ShowGameContext):
        ctx.actuators.demagnetize_all()
        ctx.score += CONFIG.BUILD_ONE_FLOOR
        time.sleep(1)
        return True


class BlockBanner(BaseTask):
    """
    Task to activate the banner-blocking actuator.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to block the banner.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.block_banner()
        return True


class DeplacementPosition(BaseTask):
    """
    Task to adjust the actuator to a predefined displacement position.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to move to a displacement position.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.deplacement_position()
        return True
    
class DeplacementObject(BaseTask):
    """
    Task to adjust the actuator to a predefined displacement position.
    """

    def handle(self, ctx: ShowGameContext) -> bool:
        """
        Execute the actuator command to move to a displacement position.

        Args:
            ctx (ShowGameContext): The current game context.

        Returns:
            bool: Always returns True after executing the action.
        """
        ctx.actuators.deplacement_object()
        return True
