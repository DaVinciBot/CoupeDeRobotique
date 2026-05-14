"""Dummy winter spatial computation for simulations."""

from __future__ import annotations

import random
from typing import TYPE_CHECKING, override

from loggerplusplus import Logger, LogLevels, log
from services.winter_spatial_computation import WinterSpatialComputation
from stuff import Crate

if TYPE_CHECKING:
    from arena.base_arena.arena import BaseArena


DEPOSIT_ZONE_START_INDEX = 11
RELEASED_CRATES_ZONE_ID = -2
DEFAULT_RELEASE_POINT = (150.0, 100.0)

DEPOSIT_ZONE_ORIENTATION: dict[int, str] = {
    11: "vertical",
    12: "horizontal",
    13: "horizontal",
    14: "horizontal",
    15: "vertical",
    16: "horizontal",
    17: "horizontal",
    18: "horizontal",
    19: "horizontal",
    20: "horizontal",
}


class WinterSpatialComputationDummy(WinterSpatialComputation):
    """Dummy version of WinterSpatialComputation for testing.

    Simulates crate positions and colors for the Winter Is Coming 2026 game.
    """

    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        lora: None = None,
        *,
        enable_dummy: bool = True,
    ) -> None:
        """Initialize the dummy spatial computation service.

        Args:
            logger (Logger): Logger used to report simulated events.
            arena (BaseArena): Arena used for position references.
            lora (None, optional): Unused LoRa placeholder. Defaults to None.
            enable_dummy (bool, optional): Whether to enable dummy mode.
                Defaults to True.
        """
        super().__init__(logger, arena, lora, enable_dummy=enable_dummy)

        self.crates_zones_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
            ((10, 130), (25, 110)),
            ((10, 50), (25, 30)),
            ((100, 25), (120, 10)),
            ((105, 87.5), (125, 72.5)),
            ((290, 130), (275, 110)),
            ((275, 50), (290, 30)),
            ((200, 25), (180, 10)),
            ((195, 87.5), (175, 72.5)),
        ]

        self.deposit_zone_points: list[
            tuple[tuple[float, float], tuple[float, float]]
        ] = [
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

        self.crates: dict[int, list[Crate]] = self._generate_fixed_crates()
        self.held_crates: list[Crate] = []
        self.robot_position: tuple[float, float, float] | None = None
        self.enemy_position: tuple[float, float, float] | None = None
        self.enemy_velocity: tuple[float, float, float] | None = None

    def _generate_fixed_crates(self) -> dict[int, list[Crate]]:
        """Generate a fixed set of crates for testing purposes.

            - For pickup zones (3 to 10), create 4 crates each, arranged in a
              line.
            - For deposit zones (11 to 20), start with no crates.
            - Alternate crate colors between blue (0) and yellow (1) for
              variety.
            - Log the initial crate distribution for debugging.
            - This setup allows testing of picking, dropping, and reversing crates
              without randomness.
            - Crate positions are determined based on pickup zone dimensions to
              ensure they fit within the area.

        Returns:
            dict[int, list[Crate]]:
                A dictionary mapping zone indices to lists of Crate objects.
        """
        crates: dict[int, list[Crate]] = {}

        crate_size = 5
        initial_fill_zones = range(3, 11)

        for zone_index in initial_fill_zones:
            color_cycle = [0, 0, 1, 1]
            random.shuffle(color_cycle)

            p1, p2 = self.crates_zones_points[
                (zone_index - 3) % len(self.crates_zones_points)
            ]
            x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
            y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])

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

            crates[zone_index] = [
                Crate(zone_index, x_positions[i], y_positions[i], color_cycle[i])
                for i in range(4)
            ]

        for zone_index in range(11, 21):
            crates[zone_index] = []

        return crates

    @override
    @log("WinterSpatialComputationDummy", LogLevels.INFO)
    def pick_crates(
        self,
        zone_id: int,
        count: int | None = None,
        color_id: int | None = None,
    ) -> None:
        """Pick up crates from the specified pickup zone.

        Args:
            zone_id (int): Index of the pickup zone from which to pick crates.
            count (int | None): Maximum number of crates to pick. ``None`` picks all.
            color_id (int | None): Color filter. ``None`` accepts all colors.
        """
        available_crates = [c for c in self.crates.get(zone_id, []) if not c.held]
        matching_crates = [
            c for c in available_crates if color_id is None or c.color_id == color_id
        ]
        picked_crates = matching_crates[:count]
        if count is None:
            picked_crates = matching_crates

        self.logger.info(
            f"Picking {len(picked_crates)} crate(s) from zone {zone_id}.",
        )
        for c in picked_crates:
            c.held = True
            c.zone_id = -1
            self.held_crates.append(c)
        self.crates[zone_id] = [c for c in available_crates if c not in picked_crates]
        self.logger.info(
            f"Now holding {len(self.held_crates)} crate(s). "
            f"Remaining zones: {list(self.crates.keys())}",
        )

    @override
    @log("WinterSpatialComputationDummy", LogLevels.INFO)
    def drop_crates(
        self,
        zone_index: int,
        count: int | None = None,
        color_id: int | None = None,
    ) -> None:
        """Drop held crates in the specified deposit zone.

        Crates are arranged in a line within the deposit zone, centered vertically.

        Args:
            zone_index (int): Index of the deposit zone where crates should be dropped.
            count (int | None): Maximum number of crates to drop. ``None`` drops all.
            color_id (int | None): Color filter. ``None`` accepts all colors.
        """
        if not self.held_crates:
            self.logger.info("No crates to drop.")
            return

        matching_crates = [
            c for c in self.held_crates if color_id is None or c.color_id == color_id
        ]
        dropped_crates = matching_crates[:count]
        if count is None:
            dropped_crates = matching_crates

        if not dropped_crates:
            self.logger.info("No matching crates to drop.")
            return

        (p1, p2) = self.deposit_zone_points[zone_index - DEPOSIT_ZONE_START_INDEX]

        x_min, x_max = min(p1[0], p2[0]), max(p1[0], p2[0])
        y_min, y_max = min(p1[1], p2[1]), max(p1[1], p2[1])

        num_crates = len(dropped_crates)
        crate_size = 5
        zone_start_index = len(self.crates.setdefault(zone_index, []))

        orientation = DEPOSIT_ZONE_ORIENTATION.get(zone_index, "horizontal")

        if orientation == "horizontal":
            x_positions = [
                x_min + crate_size / 2 + (zone_start_index + i) * crate_size
                for i in range(num_crates)
            ]
            y_positions = [(y_min + y_max) / 2] * num_crates
        else:
            x_positions = [(x_min + x_max) / 2] * num_crates
            y_positions = [
                y_min + crate_size / 2 + (zone_start_index + i) * crate_size
                for i in range(num_crates)
            ]

        for i, crate in enumerate(dropped_crates):
            crate.x = x_positions[i]
            crate.y = y_positions[i]
            crate.zone_id = zone_index
            crate.held = False
            self.crates[zone_index].append(crate)

        self.logger.info(
            f"Dropped {num_crates} crate(s) in zone {zone_index}. "
            f"Zone now has {len(self.crates[zone_index])} crate(s).",
        )
        self.held_crates = [c for c in self.held_crates if c not in dropped_crates]

    @log("WinterSpatialComputationDummy", LogLevels.INFO)
    def release_crates(
        self,
        count: int | None = None,
        color_id: int | None = None,
        point: object | None = None,
    ) -> None:
        """Release held crates outside any deposit zone.

        Args:
            count (int | None): Maximum number of crates to release.
            color_id (int | None): Color filter. ``None`` accepts all colors.
            point (object | None): Optional point with ``x`` and ``y`` attributes.
        """
        matching_crates = [
            c for c in self.held_crates if color_id is None or c.color_id == color_id
        ]
        released_crates = matching_crates[:count]
        if count is None:
            released_crates = matching_crates

        if not released_crates:
            self.logger.info("No matching crates to release.")
            return

        x_start = getattr(point, "x", DEFAULT_RELEASE_POINT[0])
        y_start = getattr(point, "y", DEFAULT_RELEASE_POINT[1])
        release_start_index = len(self.crates.setdefault(RELEASED_CRATES_ZONE_ID, []))
        crate_size = 5

        for i, crate in enumerate(released_crates):
            crate.x = x_start + (release_start_index + i) * crate_size
            crate.y = y_start
            crate.zone_id = RELEASED_CRATES_ZONE_ID
            crate.held = False
            self.crates[RELEASED_CRATES_ZONE_ID].append(crate)

        self.held_crates = [c for c in self.held_crates if c not in released_crates]
        self.logger.info(
            f"Released {len(released_crates)} crate(s) outside deposit zones.",
        )

    @override
    @log("WinterSpatialComputationDummy", LogLevels.INFO)
    def reverse_crate(self) -> None:
        """No-op: winter actuator rotation no longer changes crate colors."""
        self.logger.info("No crate color reversed in dummy simulation.")

    @override
    @log("WinterSpatialComputationDummy", LogLevels.INFO)
    def send_data(self) -> None:
        """Dummy method to send data. Logs the action without transmitting anything."""
        if self.lora is not None:
            self.lora.send("Hello from WinterSpatialComputationDummy!")
        else:
            self.logger.info(
                "WinterSpatialComputationDummy: Simulating sending data to LoRa module.",
            )

    @override

    def receive_data(self) -> dict[str, object]:
        """Dummy method to receive data. Returns simulated header and crate data.

        Returns:
            dict[str, object]: A dictionary containing simulated robot position,
                               enemy position, enemy velocity, and crates.
        """
        if self.lora is not None:
            self.lora.receive()

        self.robot_position = self.get_robot_position()
        self.enemy_position = self.get_enemy_position()
        self.enemy_velocity = self.get_enemy_velocity()

        return {
            "robot_position": self.robot_position,
            "enemy_position": self.enemy_position,
            "enemy_velocity": self.enemy_velocity,
            "crates": self.crates,
        }
