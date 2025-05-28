from controllers.actuators import ActuatorsShow
from strategy.core import BaseTask
from boombot_strategy.show_game_context import ShowGameContext


class ReadyToPickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.ready_to_pickup()
        return True


class PickUp(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.pick_up()
        return True


class Build(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.build_floors()
        return True
    
class HoldBanner(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.docking()
        return True
    
class DeployBanner(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.deploy_banner()
        return True