from dataclasses import dataclass

@dataclass
class Crate:
    zone_id: int
    x: float
    y: float
    color_id: int
    held: bool = False

    @property
    def color(self) -> str:
        return "#005B8C" if self.color_id == 0 else "#F7B500"