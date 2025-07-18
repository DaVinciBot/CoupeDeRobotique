from arena import ShowArena
from controllers import ActuatorsShow, RollingBasis
from strategy.core import BaseGameContext


class ShowGameContext(BaseGameContext):
    """Context class for the show game.

    This class is used to store the context of the show game.
    """

    def __init__(
        self,
        arena: ShowArena,
        rolling_basis: RollingBasis,
        actuators: ActuatorsShow,
        score: int = 0,
    ) -> None:
        """Initialize the ShowGameContext.

        Args:
            arena (ShowArena): The arena of the game.
            rolling_basis (RollingBasis): The rolling basis of the robot.
            actuators (ActuatorsShow): The actuators of the robot.
            score (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis = rolling_basis
        self.actuators: ActuatorsShow = actuators
        self.score = score
