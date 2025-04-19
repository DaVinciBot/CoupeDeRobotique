from strategy import BaseGameContext
from arena import ShowArena
from controllers import RollingBasis, Actuators


class ShowGameContext(BaseGameContext):
    def __init__(
        self, arena: ShowArena, rolling_basis: RollingBasis, actuators: Actuators
    ) -> None:
        super().__init__(arena)
        self.rolling_basis: RollingBasis = rolling_basis
        self.actuators: Actuators = actuators
