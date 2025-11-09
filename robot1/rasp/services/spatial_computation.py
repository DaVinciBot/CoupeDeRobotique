from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from controllers.rolling_basis import RollingBasis, RollingBasisDummy
from common.arena.base_arena.arena import BaseArena
from geometry import OrientedPoint

if TYPE_CHECKING:
    from loggerplusplus import Logger


class SpatialComputation:
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
        Send data to the LoRa module.

        This is a placeholder method and should be implemented with actual
        LoRa communication logic.
        """
        data = struct.pack(
            "<9f",
            *self.get_robot_position(),
            *self.get_enemy_position(),
            *self.get_enemy_velocity(),
        )

        self.lora.send(data)  # Placeholder for sending data via LoRa

    def receive_data(self) -> tuple[float, float, float, float, float, float, float, float, float]:
        """
        Receive data from the LoRa module.

        This is a placeholder method and should be implemented with actual
        LoRa communication logic.
        """
        data = self.lora.receive()

        unpacked_data = struct.unpack("<9f", data)
        robot_x, robot_y, robot_theta, enemy_x, enemy_y, enemy_t, enemy_dx, enemy_dy, enemy_speed = unpacked_data

        return robot_x, robot_y, robot_theta, enemy_x, enemy_y, enemy_t, enemy_dx, enemy_dy, enemy_speed
