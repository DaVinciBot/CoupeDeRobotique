from __future__ import annotations

import struct
from typing import TYPE_CHECKING, Dict, List, override

from services import SpatialComputation
from common.stuff import Crate

from a_config_loader import CONFIG

if TYPE_CHECKING:
    from loggerplusplus import Logger
    from common.arena.base_arena.arena import BaseArena

NUM_CRATES = 32
CRATE_FORMAT = "b2hB"

HEADER_FORMAT = CONFIG.SPATIAL_COMPUTATION_HEADER["format"]
PACKET_FORMAT = HEADER_FORMAT + CRATE_FORMAT * NUM_CRATES


class WinterSpatialComputation(SpatialComputation):
    def __init__(
        self,
        logger: Logger,
        arena: BaseArena,
        lora: None = None,
        enable_dummy: bool = False,
    ) -> None:
        super().__init__(logger, arena, lora, enable_dummy)
        self.crates: Dict[int, List[Crate]] = {}

    def pick_crates(self, zone_id: int) -> None:
        pass

    def drop_crates(self, zone_index: int) -> None:
        pass

    def reverse_crate(self) -> None:
        pass

    @override
    def receive_data(self) -> dict[str, object]:
        data = self.lora.receive()
        unpacked = struct.unpack(PACKET_FORMAT, data)

        result = self._unpack_header(unpacked)

        self.crates = {}
        offset = 9
        fields_per_crate = 4

        for i in range(NUM_CRATES):
            base = offset + i * fields_per_crate
            zone_id, x_enc, y_enc, color = unpacked[base:base + fields_per_crate]
            zone_id = int(zone_id)
            crate = Crate(zone_id, self._dec_xy(x_enc), self._dec_xy(y_enc), int(color))
            self.crates.setdefault(zone_id, []).append(crate)

        return {**result, "crates": self.crates}
