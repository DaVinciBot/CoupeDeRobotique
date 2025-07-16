from arena import ShowArena
from controllers import ActuatorsShow, RollingBasis
from strategy.core import BaseGameContext


class ShowGameContext(BaseGameContext):
    def __init__(
        self,
        arena: ShowArena,
        rolling_basis: RollingBasis,
        actuators: ActuatorsShow = None,
        score: int = 0,
    ) -> None:
        super().__init__(arena)
        self.rolling_basis: RollingBasis = rolling_basis
        self.actuators: ActuatorsShow = actuators
        self.score = score
