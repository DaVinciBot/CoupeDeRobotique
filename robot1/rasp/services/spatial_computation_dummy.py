from __future__ import annotations
from __future__ import annotations

import random
from math import pi
from typing import TYPE_CHECKING

from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from common.arena.base_arena.arena import BaseArena
from geometry import OrientedPoint

if TYPE_CHECKING:
    from loggerplusplus import Logger


class SpatialComputationDummy:
    """
    Dummy version of SpatialComputation for testing without LoRa or RollingBasis.
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

    def get_robot_position(self) -> tuple[float, float, float]:
        """
        Get the robot's current position in the global coordinate system.

        Returns:
            A tuple containing the (x, y, theta) coordinates of the robot.
        """
        robot_odometrie: OrientedPoint = self.rolling_basis.odometrie
        return robot_odometrie.x, robot_odometrie.y, robot_odometrie.theta

    def get_enemy_position(self) -> tuple[float, float, float]:
        """
        Get the enemy robot's current position in the global coordinate system.

        Returns:
            A tuple containing the (x, y) coordinates of the enemy robot.
        """
        enemy_point: OrientedPoint = self.arena.enemy_zone.point
        return enemy_point.x, enemy_point.y, enemy_point.theta

    def get_enemy_velocity(self) -> tuple[float, float, float]:
        """
        Get the enemy robot's current velocity.

        Returns:
            The velocity of the enemy robot.
        """
        enemy_velocity = self.arena.enemy_zone.speed_vector
        enemy_velocity_x = enemy_velocity.factored_dx
        enemy_velocity_y = enemy_velocity.factored_dy
        enemy_velocity_magnitude = enemy_velocity.speed

        return enemy_velocity_x, enemy_velocity_y, enemy_velocity_magnitude

    # Section full freestyle au cas où on envoie directement le lora d'ici, j'en sais rien ALED
    def send_data(self) -> None:
        """
        Dummy method to send data to the LoRa module.
        """
        pass

    def receive_data(self) -> dict[str, object]:
        """
        Dummy method to receive data from the LoRa module.

        Returns:
            A dictionary containing the robot's position, enemy position,
            enemy velocity, and a list of crates with their positions and color IDs.
        """

        num_crates = 48  # add to config loader

        # Simulate received data

        # Main Robot
        robot_x = random.randint(0, self.arena.width)
        robot_y = random.randint(0, self.arena.height)
        robot_theta = random.randint(0, 360) * pi / 180

        # Enemy Position
        enemy_x = random.randint(0, self.arena.width)
        enemy_y = random.randint(0, self.arena.height)
        enemy_t = random.randint(0, 360) * pi / 180

        # Enemy Velocity
        enemy_dx = random.randint(-20, 20)
        enemy_dy = random.randint(-20, 20)
        enemy_speed = int((enemy_dx ** 2 + enemy_dy ** 2) ** 0.5)

        # Crates
        crates = []
        for i in range(num_crates):
            crate_x = random.randint(0, self.arena.width)
            crate_y = random.randint(0, self.arena.height)
            crate_z = random.randint(0, 3)
            color_id = random.randint(0, 2)
            crates.append((crate_x, crate_y, crate_z, int(color_id)))

        return {
            "robot_position": (robot_x, robot_y, robot_theta),
            "enemy_position": (enemy_x, enemy_y, enemy_t),
            "enemy_velocity": (enemy_dx, enemy_dy, enemy_speed),
            "crates": crates,
        }
