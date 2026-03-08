from __future__ import annotations

import struct
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from loggerplusplus import Logger

    from common.arena.base_arena.arena import BaseArena
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy
    from geometry import OrientedPoint


class Crate:
    def __init__(self, global_id: int, zone_id: int, x: float, y: float, theta: float, color: int):
        self.id = global_id
        self.zone_id = zone_id
        self.x = x
        self.y = y
        self.theta = theta
        self.color = color
        self.held = False


class SpatialComputation:
    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        rolling_basis: RollingBasis | RollingBasisDummy,
        lora: None = None,  # Lora parameters maybe added later
        enable_dummy: bool = False
    ) -> None:
        self.logger = logger
        self.arena = arena
        self.rolling_basis = rolling_basis
        self.lora = lora  # Placeholder for LoRa module

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

        self.crates: Dict[int, List[Crate]] = {}
        self.held_crates: List[Crate] = []

        crate_id = 1
        crates_per_zone = 4
        for zone_index in range(8):
            self.crates[zone_index] = []
            for i in range(crates_per_zone):
                cid = i
                self.crates[zone_index].append(Crate(crate_id, cid, 0.0, 0.0, 0.0, 0))
                crate_id += 1

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

    def pick_crates(self, zone_id: int) -> None:
        pass

    def drop_crates(self, zone_index: int) -> None:
        pass

    def reverse_crate(self, crate_id: str) -> None:
        pass

    # Section full freestyle au cas où on envoie directement le lora d'ici, j'en sais rien ALED
    def send_data(self) -> None:
        """Send data to the LoRa module.

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

    def receive_data(self) -> dict[str, object]:
        """Receive data from the LoRa module.

        This is a placeholder method and should be implemented with actual
        LoRa communication logic.

        Returns:
            A dictionary containing the robot's position, enemy position,
            enemy velocity, and a list of crates with their positions and color IDs.
        """
        data = self.lora.receive()

        num_crates = 32  # add to config loader

        data_format = "<9f{}f".format(num_crates * 4)
        unpacked_data = struct.unpack(data_format, data)

        # Main Robot
        self.robot_position = tuple(unpacked_data[0:3])

        # Enemy Position
        self.enemy_position = tuple(unpacked_data[3:6])

        # Enemy Velocity
        self.enemy_velocity = tuple(unpacked_data[6:9])

        # Crates
        for i in range(num_crates):
            base = 9 + i * 4
            crate_x, crate_y, crate_z, color_id = unpacked_data[base: base + 4]
            zone_index = i // 4
            crate_in_zone_index = i % 4
            crate_obj = self.crates[zone_index][crate_in_zone_index]
            crate_obj.x = crate_x
            crate_obj.y = crate_y
            crate_obj.theta = crate_z
            crate_obj.color = int(color_id)

        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
            "crates": self.crates,
        }
