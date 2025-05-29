from config_loader import CONFIG

import time
from strategy.core import BaseTask
from boombot_strategy.show_game_context import ShowGameContext


class ReadyToApproachToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.ready_to_approach_to_pickup()
        return True


class PrepareToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.prepare_to_pickup()
        time.sleep(1)
        return True


class PickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.pickup()
        time.sleep(2)
        return True


class Build(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.build()
        ctx.score += CONFIG.BUILD_TWO_FLOORS
        time.sleep(2)
        return True


class BlockBanner(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.block_banner()
        return True
