from controllers.actuators import ActuatorsShow
from strategy.core import BaseTask
from boombot_strategy.show_game_context import ShowGameContext
from loggerplusplus import Logger


class ReadyToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.ready_to_pickup()
        self.logger.info("Ready to pick up action executed")
        return True


class PickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.pick_up()
        self.logger.info("Pick up action executed")
        return True


class Build(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.build_floors()
        self.logger.info("Build action executed")
        return True
