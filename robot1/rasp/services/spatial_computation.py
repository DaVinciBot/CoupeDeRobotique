from __future__ import annotations

import struct
from typing import TYPE_CHECKING, Dict, List

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from common.arena.base_arena.arena import BaseArena
    from controllers.rolling_basis import RollingBasis, RollingBasisDummy
    from geometry import OrientedPoint

NUM_CRATES = 32
CRATE_FORMAT = "b3fB"  # Askip, j'avoue je suis pas calée : zone_id(int8), x, y, theta (float32), color(uint8)
PACKET_FORMAT = "<9f" + CRATE_FORMAT * NUM_CRATES


class Crate:
    def __init__(self, zone_id: int, x: float, y: float, theta: float, color: int):
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
        lora: None = None,
        enable_dummy: bool = False
    ) -> None:
        self.logger = logger
        self.arena = arena
        self.rolling_basis = rolling_basis
        self.lora = lora

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

        self.crates: Dict[int, List[Crate]] = {}
        self.held_crates: List[Crate] = []

    def get_robot_position(self) -> tuple[float, float, float]:
        robot_odometrie: OrientedPoint = self.rolling_basis.odometrie
        self.robot_position = (robot_odometrie.x, robot_odometrie.y, robot_odometrie.theta)
        return self.robot_position

    def get_enemy_position(self) -> tuple[float, float, float]:
        enemy_point: OrientedPoint = self.arena.enemy_zone.point
        self.enemy_position = (enemy_point.x, enemy_point.y, enemy_point.theta)
        return self.enemy_position

    def get_enemy_velocity(self) -> tuple[float, float, float]:
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

    def reverse_crate(self) -> None:
        pass

    def send_data(self) -> None:
        data = struct.pack(
            "<9f",
            *self.get_robot_position(),
            *self.get_enemy_position(),
            *self.get_enemy_velocity(),
        )
        self.lora.send(data)

    def receive_data(self) -> dict[str, object]:
        data = self.lora.receive()
        unpacked = struct.unpack(PACKET_FORMAT, data)

        self.robot_position = tuple(unpacked[0:3])
        self.enemy_position = tuple(unpacked[3:6])
        self.enemy_velocity = tuple(unpacked[6:9])

        self.crates = {}
        offset = 9
        fields_per_crate = 5

        for i in range(NUM_CRATES):
            base = offset + i * fields_per_crate
            zone_id, x, y, theta, color = unpacked[base:base + fields_per_crate]
            zone_id = int(zone_id)
            crate = Crate(zone_id, x, y, theta, int(color))
            self.crates.setdefault(zone_id, []).append(crate)

        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
            "crates": self.crates,
        }
