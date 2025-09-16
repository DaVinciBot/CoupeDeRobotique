"""Game context used by the demo strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core import BaseGameContext

if TYPE_CHECKING:
    from arena import ShowArena
    from controllers import (
        ActuatorsShow,
        ActuatorsShowDummy,
        RollingBasis,
        RollingBasisDummy,
    )


class ShowGameContext(BaseGameContext):
    """Context class for the show game.

    This class is used to store the context of the show game.
    """

    def __init__(
        self,
        arena: ShowArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        actuators: ActuatorsShow | ActuatorsShowDummy,
        score: int = 0,
    ) -> None:
        """Initialize the ShowGameContext.

        Args:
            arena (ShowArena): The arena of the game.
            rolling_basis (RollingBasis | RollingBasisDummy):
                The rolling basis of the robot.
            actuators (ActuatorsShow | ActuatorsShowDummy): The actuators of the robot.
            score (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsShow | ActuatorsShowDummy = actuators
        self.score = score
