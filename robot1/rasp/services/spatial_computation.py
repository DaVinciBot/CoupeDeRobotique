"""Spatial computation service for packing and decoding LoRa data."""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING

from loggerplusplus import LogLevels, log

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
    """Base spatial computation service shared by arena implementations."""

    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        lora: None = None,
        *,
        enable_dummy: bool = False,
    ) -> None:
        """Initialize the spatial computation service.

        Args:
            logger (Logger): Logger used for diagnostics.
            arena (BaseArena): Arena used to retrieve positions.
            lora (None, optional): LoRa communication handler. Defaults to None.
            enable_dummy (bool, optional): Enable dummy mode when True.
                Defaults to False.
        """
        self.logger = logger
        self.arena = arena
        self.lora = lora
        self.enable_dummy = enable_dummy

        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

    @staticmethod
    def _enc_xy(v: float) -> int:
        return round(v * XY_FACTOR)

    @staticmethod
    def _enc_angle(v: float) -> int:
        return round(v * ANGLE_FACTOR)

    @staticmethod
    def _dec_xy(v: int) -> float:
        return v / XY_FACTOR

    @staticmethod
    def _dec_angle(v: int) -> float:
        return v / ANGLE_FACTOR

    def get_robot_position(self) -> tuple[float, float, float]:
        """Return the current robot position from the arena.

        Returns:
            tuple[float, float, float]: Robot (x, y, theta) position.
        """
        robot_point: OrientedPoint = self.arena.ally_zone.point
        self.robot_position = (robot_point.x, robot_point.y, robot_point.theta)
        return self.robot_position

    def get_enemy_position(self) -> tuple[float, float, float]:
        """Return the current enemy position from the arena.

        Returns:
            tuple[float, float, float]: Enemy (x, y, theta) position.
        """
        enemy_point: OrientedPoint = self.arena.enemy_zone.point
        self.enemy_position = (enemy_point.x, enemy_point.y, enemy_point.theta)
        return self.enemy_position

    def get_enemy_velocity(self) -> tuple[float, float, float]:
        """Return the current enemy velocity from the arena.

        Returns:
            tuple[float, float, float]: Enemy velocity (dx, dy, speed).
        """
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
            self._enc_xy(rx),
            self._enc_xy(ry),
            self._enc_angle(rtheta),
            self._enc_xy(ex),
            self._enc_xy(ey),
            self._enc_angle(etheta),
            self._enc_xy(evx),
            self._enc_xy(evy),
            self._enc_xy(espeed),
        )

    def _unpack_header(self, unpacked: tuple) -> dict[str, object]:
        self.robot_position = (
            self._dec_xy(unpacked[0]),
            self._dec_xy(unpacked[1]),
            self._dec_angle(unpacked[2]),
        )
        self.enemy_position = (
            self._dec_xy(unpacked[3]),
            self._dec_xy(unpacked[4]),
            self._dec_angle(unpacked[5]),
        )
        self.enemy_velocity = (
            self._dec_xy(unpacked[6]),
            self._dec_xy(unpacked[7]),
            self._dec_xy(unpacked[8]),
        )
        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
        }

    @log("SpatialComputation", LogLevels.DEBUG)
    def send_data(self) -> None:
        """Send the packed header over LoRa."""
        self.lora.send(self._pack_header())

    @log("SpatialComputation", LogLevels.DEBUG)
    def receive_data(self) -> dict[str, object]:
        """Receive and unpack header data from LoRa.

        Returns:
            dict[str, object]: Unpacked header fields as a dictionary.
        """
        data = self.lora.receive()
        unpacked = struct.unpack(HEADER_FORMAT, data)
        return self._unpack_header(unpacked)
