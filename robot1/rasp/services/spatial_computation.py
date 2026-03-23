from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from a_config_loader import CONFIG

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from common.arena.base_arena.arena import BaseArena
    from geometry import OrientedPoint

HEADER_FORMAT = CONFIG.SPATIAL_COMPUTATION_HEADER["format"]
HEADER_SIZE = struct.calcsize(HEADER_FORMAT)

XY_FACTOR = CONFIG.SPATIAL_COMPUTATION_HEADER["xy_factor"]
ANGLE_FACTOR = CONFIG.SPATIAL_COMPUTATION_HEADER["angle_factor"]


class SpatialComputation:
    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        lora: None = None,
        enable_dummy: bool = False,
    ) -> None:
        self.logger = logger
        self.arena = arena
        self.lora = lora

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

    @staticmethod
    def _enc_xy(v: float) -> int:
        return int(round(v * XY_FACTOR))

    @staticmethod
    def _enc_angle(v: float) -> int:
        return int(round(v * ANGLE_FACTOR))

    @staticmethod
    def _dec_xy(v: int) -> float:
        return v / XY_FACTOR

    @staticmethod
    def _dec_angle(v: int) -> float:
        return v / ANGLE_FACTOR

    def get_robot_position(self) -> tuple[float, float, float]:
        robot_point: OrientedPoint = self.arena.ally_zone.point
        self.robot_position = (robot_point.x, robot_point.y, robot_point.theta)
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

    def _pack_header(self) -> bytes:
        rx, ry, rtheta = self.get_robot_position()
        ex, ey, etheta = self.get_enemy_position()
        evx, evy, espeed = self.get_enemy_velocity()
        return struct.pack(
            HEADER_FORMAT,
            self._enc_xy(rx), self._enc_xy(ry), self._enc_angle(rtheta),
            self._enc_xy(ex), self._enc_xy(ey), self._enc_angle(etheta),
            self._enc_xy(evx), self._enc_xy(evy), self._enc_xy(espeed),
        )

    def _unpack_header(self, unpacked: tuple) -> dict[str, object]:
        self.robot_position = (
            self._dec_xy(unpacked[0]), self._dec_xy(unpacked[1]), self._dec_angle(unpacked[2])
        )
        self.enemy_position = (
            self._dec_xy(unpacked[3]), self._dec_xy(unpacked[4]), self._dec_angle(unpacked[5])
        )
        self.enemy_velocity = (
            self._dec_xy(unpacked[6]), self._dec_xy(unpacked[7]), self._dec_xy(unpacked[8])
        )
        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
        }

    def send_data(self) -> None:
        self.lora.send(self._pack_header())

    def receive_data(self) -> dict[str, object]:
        data = self.lora.receive()
        unpacked = struct.unpack(HEADER_FORMAT, data)
        return self._unpack_header(unpacked)
