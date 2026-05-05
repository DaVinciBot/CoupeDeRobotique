"""Winter-specific spatial computation implementation."""

from __future__ import annotations

import struct
from typing import TYPE_CHECKING, override

from loggerplusplus import LogLevels, log
from services.spatial_computation import SpatialComputation
from stuff import Crate

from a_config_loader import CONFIG

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from lora_com import LoraCom

    from arena.base_arena.arena import BaseArena

NUM_CRATES = 32
CRATE_FORMAT = "b2hB"

PACKET_FORMAT = CONFIG.SPATIAL_COMPUTATION_HEADER_FORMAT + CRATE_FORMAT * NUM_CRATES


class WinterSpatialComputation(SpatialComputation):
    """Spatial computation for the Winter game packet format."""

    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        lora: LoraCom | None = None,
        *,
        enable_dummy: bool = False,
    ) -> None:
        """Initialize the winter spatial computation service.

        Args:
            logger (Logger): Logger used for diagnostics.
            arena (BaseArena): Arena providing positions.
            lora (LoraCom | None, optional): LoRa communication handler.
                Defaults to None.
            enable_dummy (bool, optional): Enable dummy mode when True.
                Defaults to False.
        """
        super().__init__(logger, arena, lora, enable_dummy=enable_dummy)
        self.crates: dict[int, list[Crate]] = {}

    @log("WinterSpatialComputation", LogLevels.DEBUG)
    def pick_crates(self, zone_id: int) -> None:
        """Pick up crates from a pickup zone.

        Args:
            zone_id (int): Index of the pickup zone.
        """

    @log("WinterSpatialComputation", LogLevels.DEBUG)
    def drop_crates(self, zone_index: int) -> None:
        """Drop held crates into a deposit zone.

        Args:
            zone_index (int): Index of the deposit zone.
        """

    @log("WinterSpatialComputation", LogLevels.DEBUG)
    def reverse_crate(self) -> None:
        """Reverse held crates to match team color."""

    @override
    @log("WinterSpatialComputation", LogLevels.DEBUG)
    def receive_data(self) -> dict[str, object]:
        """Receive, unpack, and store crate data from LoRa.

        Returns:
            dict[str, object]: Header data merged with decoded crate mapping.
        """
        if self.lora is None:
            self.logger.warning("No LoRa module configured, cannot receive data.")
            return {"crates": self.crates}

        data = self.lora.receive()
        unpacked = struct.unpack(PACKET_FORMAT, data)

        result = self._unpack_header(unpacked)

        self.crates = {}
        offset = 9
        fields_per_crate = 4

        for i in range(NUM_CRATES):
            base = offset + i * fields_per_crate
            zone_id, x_enc, y_enc, color = unpacked[base: base + fields_per_crate]
            zone_id = int(zone_id)
            crate = Crate(zone_id, self._dec_xy(x_enc), self._dec_xy(y_enc), int(color))
            self.crates.setdefault(zone_id, []).append(crate)

        return {**result, "crates": self.crates}
