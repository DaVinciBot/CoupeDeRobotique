from strategy.core import BaseGameContext
from arena import ShowArena
from controllers import RollingBasis, ActuatorsShow


class ShowGameContext(BaseGameContext):
    def __init__(
        self, arena: ShowArena, rolling_basis: RollingBasis, actuators: ActuatorsShow = None
    ) -> None:
        super().__init__(arena)
        self.rolling_basis: RollingBasis = rolling_basis
        self.actuators: ActuatorsShow = actuators
