from __future__ import annotations

import random
from math import pi
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from common.arena.base_arena.arena import BaseArena
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy
    from geometry import OrientedPoint


class SpatialComputationDummy:
    """Dummy version of SpatialComputation for testing without LoRa or RollingBasis.

    All methods exist but return placeholder data.
    """

    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        lora: None = None,  # Lora parameters maybe added later
    ) -> None:
        self.logger = logger
        self.arena = arena
        self.rolling_basis = rolling_basis
        self.lora = lora  # Placeholder for LoRa module

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

        self.crates = self._generate_fixed_crates()

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

    def _generate_fixed_crates(self) -> list[tuple[float, float, float, int]]:
        """Generate a fixed list of crate positions and color IDs.

        Returns:
            list[tuple[float, float, float, int]]:
                List of tuples containing (x, y, z, color_id) for each crate.
        """
        crates = []
        crate_size = 5
        for p1, p2 in self.crates_zones_points:
            x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
            y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])
            color_ids = [0, 0, 1, 1]
            random.shuffle(color_ids)

            if (x_max - x_min) >= (y_max - y_min):
                x_positions = [
                    x_min + crate_size / 2 + i * crate_size for i in range(4)
                ]
                y_positions = [(y_min + y_max) / 2] * 4
            else:
                x_positions = [(x_min + x_max) / 2] * 4
                y_positions = [
                    y_min + crate_size / 2 + i * crate_size for i in range(4)
                ]

            for i in range(4):
                crates.append((x_positions[i], y_positions[i], 0, color_ids[i]))

        return crates

    def get_robot_position(self) -> tuple[float, float, float]:
        """Get the robot's current position in the global coordinate system.

        Returns:
            A tuple containing the (x, y, theta) coordinates of the robot.
        """
        robot_odometrie: OrientedPoint = self.rolling_basis.odometrie
        self.robot_position = (robot_odometrie.x, robot_odometrie.y, robot_odometrie.theta)
        return self.robot_position

    def get_enemy_position(self) -> tuple[float, float, float]:
        """Get the enemy robot's current position in the global coordinate system.

        Returns:
            A tuple containing the (x, y) coordinates of the enemy robot.
        """
        enemy_point: OrientedPoint = self.arena.enemy_zone.point
        self.enemy_position = (enemy_point.x, enemy_point.y, enemy_point.theta)
        return self.enemy_position

    def get_enemy_velocity(self) -> tuple[float, float, float]:
        """Get the enemy robot's current velocity.

        Returns:
            The velocity of the enemy robot.
        """
        enemy_velocity = self.arena.enemy_zone.speed_vector
        self.enemy_velocity = (
            enemy_velocity.factored_dx,
            enemy_velocity.factored_dy,
            enemy_velocity.speed,
        )
        return self.enemy_velocity

    def send_data(self) -> None:
        """Dummy method to send data to the LoRa module."""

    def receive_data(self) -> dict[str, object]:
        """Dummy method to receive data from the LoRa module.

        Returns:
            dict[str, object]:
                A dictionary containing the robot's position, enemy position,
                enemy velocity, and a list of crates with their positions and color IDs.
        """
        # Simulate received data

        # Main Robot
        self.robot_position = (
            random.randint(0, self.arena.width),
            random.randint(0, self.arena.height),
            random.randint(0, 360) * pi / 180,
        )

        # Enemy Position
        self.enemy_position = (
            random.randint(0, self.arena.width),
            random.randint(0, self.arena.height),
            random.randint(0, 360) * pi / 180,
        )

        # Enemy Velocity
        enemy_dx = random.randint(-20, 20)
        enemy_dy = random.randint(-20, 20)
        enemy_speed = int((enemy_dx ** 2 + enemy_dy ** 2) ** 0.5)
        self.enemy_velocity = (enemy_dx, enemy_dy, enemy_speed)

        # Crates
        # self.crates = self.crates

        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
            "crates": self.crates,
        }
