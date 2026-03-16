from __future__ import annotations

import random
from math import pi
from typing import TYPE_CHECKING
from services import SpatialComputation, Crate

from typing import override, Dict, List

from loggerplusplus import Logger, log

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from common.arena.base_arena.arena import BaseArena
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy
    from geometry import OrientedPoint


class SpatialComputationDummy(SpatialComputation):
    """Dummy version of SpatialComputation for testing without LoRa or RollingBasis.

    All methods exist but return placeholder data.
    """

    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        lora: None = None,  # Lora parameters maybe added later
        enable_dummy: bool = True
    ) -> None:

        super().__init__(logger, arena, rolling_basis, lora, enable_dummy)

        self.crates_zones_points = [
            ((10, 130), (25, 110)),
            ((10, 50), (25, 30)),
            ((100, 25), (120, 10)),
            ((105, 87.5), (125, 72.5)),
            ((290, 130), (275, 110)),
            ((275, 50), (290, 30)),
            ((200, 25), (180, 10)),
            ((195, 87.5), (175, 72.5)),
        ]

        self.deposit_zone_points = [
            ((0, 70), (20, 90)),
            ((60, 20), (80, 0)),
            ((115, 155), (135, 135)),
            ((70, 90), (90, 70)),
            ((300, 90), (280, 70)),
            ((240, 20), (220, 0)),
            ((185, 155), (165, 135)),
            ((230, 90), (210, 70)),
            ((140, 90), (160, 70)),
            ((140, 20), (160, 0)),
        ]

        self.crates: Dict[int, List[Crate]] = self._generate_fixed_crates()

        self.held_crates: List[Crate] = []

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

    def _generate_fixed_crates(self) -> Dict[int, list[Crate]]:
        """
        Generate a fixed list of crate positions and color IDs.

        Returns:
            Dict[int, list[Crate]]: A dictionary mapping zone indices to lists of Crate objects
                                     representing the crates in each zone.
        """
        crates = {}
        crate_size = 5

        for zone_index, (p1, p2) in enumerate(self.crates_zones_points):
            x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
            y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])

            if (x_max - x_min) >= (y_max - y_min):
                x_positions = [x_min + crate_size / 2 + i * crate_size for i in range(4)]
                y_positions = [(y_min + y_max) / 2] * 4
            else:
                x_positions = [(x_min + x_max) / 2] * 4
                y_positions = [y_min + crate_size / 2 + i * crate_size for i in range(4)]

            colors = [0, 0, 1, 1]
            crates[zone_index] = [
                Crate(zone_index, x_positions[i], y_positions[i], -pi, colors[i])
                for i in range(4)
            ]

        return crates

    @override
    @log("DummySpatialComputation")
    def pick_crates(self, zone_id: int) -> None:
        """
        Pick up crates from the specified pickup zone.
        Args:
            zone_id (int): Index of the pickup zone from which to pick crates.
        Returns:
            None
        """
        self.logger.info(f"DummySpatialComputation: Simulating picking crates from zone {zone_id}.")
        zone_crates = [c for c in self.crates.get(zone_id, []) if not c.held]
        for c in zone_crates:
            c.held = True
            self.held_crates.append(c)
        self.crates.pop(zone_id, None)

    @override
    @log("DummySpatialComputation")
    def drop_crates(self, zone_index: int) -> None:
        """
        Drop held crates in the specified deposit zone.
        Crates are arranged in a line within the deposit zone, centered vertically.
        Args:
            zone_index (int): Index of the deposit zone where crates should be dropped.
        Returns:
            None
        """
        self.logger.info(f"DummySpatialComputation: Simulating dropping crates in deposit zone {zone_index}.")

        if not self.held_crates:
            return

        (x_min, x_max), (y_min, y_max) = self.deposit_zone_points[zone_index]

        num_crates = len(self.held_crates)
        crate_size = 5

        if (x_max - x_min) >= (y_max - y_min):
            x_positions = [x_min + crate_size / 2 + i * crate_size for i in range(num_crates)]
            y_positions = [(y_min + y_max) / 2] * num_crates
        else:
            x_positions = [(x_min + x_max) / 2] * num_crates
            y_positions = [y_min + crate_size / 2 + i * crate_size for i in range(num_crates)]

        for i, crate in enumerate(self.held_crates):
            crate.x = x_positions[i]
            crate.y = y_positions[i]
            crate.zone_id = -1
            crate.held = False

        self.held_crates = []

    @override
    @log("DummySpatialComputation")
    def reverse_crate(self) -> None:
        """
        Reverse the color of held crates that don't match the team color.
        Returns:
            None
        """
        self.logger.info("DummySpatialComputation: Simulating reversing crates not matching team color.")

        team_color_int = 1 if self.arena.team_color == self.arena.team_color.YELLOW else 0

        for crate in self.held_crates:
            if crate.color != team_color_int:
                crate.color = team_color_int

    @override
    def __str__(self) -> str:
        """Return the class name for logging.

        Returns:
            str: The class name.
        """
        return self.__class__.__name__

    @override
    @log("DummySpatialComputation")
    def send_data(self) -> None:
        """
        Dummy method to send data to the LoRa module.
        Returns:
            None
        """
        self.logger.info("DummySpatialComputation: Simulating sending data to LoRa module.")

    @override
    @log("DummySpatialComputation")
    def receive_data(self) -> dict[str, object]:
        """Dummy method to receive data from the LoRa module.

        Returns:
            dict[str, object]:
                A dictionary containing the robot's position, enemy position,
                enemy velocity, and a list of crates with their positions and color IDs.
        """
        # Simulate received data

        # Main Robot
        self.robot_position = self.get_robot_position()
        # Enemy Position
        self.enemy_position = self.get_enemy_position()
        # Enemy Velocity
        self.enemy_velocity = self.get_enemy_velocity()

        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
            "crates": self.crates,
        }
