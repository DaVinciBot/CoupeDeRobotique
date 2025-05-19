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
        ctx.actuators.build()
        return True

class EndBuild(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.end_build()
        return True
    
class InitActuator(BaseTask):
    def handle(self, ctx: ShowGameContext):
        ctx.actuators.init_actuator()
        return True