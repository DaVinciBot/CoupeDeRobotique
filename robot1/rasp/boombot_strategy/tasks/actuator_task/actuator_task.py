from config_loader import CONFIG
from controllers.actuators import ActuatorsShow
from strategy.core import BaseTask
from boombot_strategy.show_game_context import ShowGameContext
from loggerplusplus import Logger


class ReadyToApproachToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.ready_to_approach_to_pickup()
        return True


class PrepareToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.prepare_to_pickup()
        return True


class PickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.pickup()
        return True


class Build(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.build()
        ctx.score += CONFIG.BUILD_TWO_FLOORS
        return True


class BlockBanner(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.block_banner()
        return True
