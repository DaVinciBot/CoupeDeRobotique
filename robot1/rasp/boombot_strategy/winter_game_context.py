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
        actuators: ActuatorsWinter | ActuatorsWinterDummy,
        spatial_computation: (
            WinterSpatialComputation | WinterSpatialComputationDummy | None
        ) = None,
        point: int | None = None,
        score: int | None = None,
    ) -> None:
        """Initialize the WinterGameContext.

        Args:
            arena (WinterArena): The arena of the game.
            rolling_basis (RollingBasis | RollingBasisDummy):
                The rolling basis of the robot.
            actuators (ActuatorsWinter | ActuatorsWinterDummy):
                The actuators of the robot.
            spatial_computation (WinterSpatialComputation | WinterSpatialComputationDummy):
                Spatial computation service used by the robot.
            point (int | None, optional): The score of the robot.
            score (int, optional): The score of the robot. Defaults to 0.
        """
        super().__init__(arena)
        self.rolling_basis: RollingBasis | RollingBasisDummy = rolling_basis
        self.actuators: ActuatorsWinter | ActuatorsWinterDummy = actuators
        self.spatial_computation: (
            WinterSpatialComputation | WinterSpatialComputationDummy | None
        ) = spatial_computation
        self._score = (
            point if point is not None else (score if score is not None else 0)
        )

    @property
    def point(self) -> int:
        return self._score

    @point.setter
    def point(self, value: int) -> None:
        self._score = value

    @property
    def score(self) -> int:
        return self._score

    @score.setter
    def score(self, value: int) -> None:
        self._score = value
