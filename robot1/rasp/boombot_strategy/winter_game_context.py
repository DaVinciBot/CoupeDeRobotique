"""Game context used by the demo strategies."""

from __future__ import annotations

from typing import TYPE_CHECKING

from strategy.core import BaseGameContext

if TYPE_CHECKING:
    from services import WinterSpatialComputation, WinterSpatialComputationDummy

    from arena.winter_arena import WinterArena
    from controllers.actuators import ActuatorsWinter, ActuatorsWinterDummy
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy


class WinterGameContext(BaseGameContext):
    """Context class for the show game.

    This class is used to store the context of the show game.
    """

    def __init__(
        self,
        arena: WinterArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
<<<<<<< HEAD
        actuators: ActuatorsWinter | ActuatorsWinterDummy,
        point: int = 0,
=======
        actuators: ActuatorsShow | ActuatorsShowDummy,
        spatial_computation: WinterSpatialComputation | WinterSpatialComputationDummy,
        score: int = 0,
>>>>>>> origin/dev-cd
    ) -> None:
        """Initialize the WinterGameContext.

        Args:
            arena (WinterArena): The arena of the game.
            rolling_basis (RollingBasis | RollingBasisDummy):
                The rolling basis of the robot.
<<<<<<< HEAD
            actuators (ActuatorsWinter | ActuatorsWinterDummy):
                The actuators of the robot.
            point (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsWinter | ActuatorsWinterDummy = actuators
        self.point = point
=======
            actuators (ActuatorsShow | ActuatorsShowDummy): The actuators of the robot.
            spatial_computation (WinterSpatialComputation | WinterSpatialComputationDummy):
                Spatial computation service used by the robot.
            score (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsShow | ActuatorsShowDummy = actuators
        self.spatial_computation: (
            WinterSpatialComputation | WinterSpatialComputationDummy
        ) = spatial_computation
        self.score = score
>>>>>>> origin/dev-cd
