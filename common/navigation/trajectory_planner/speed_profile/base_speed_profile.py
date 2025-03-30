from abc import ABC, abstractmethod


class BaseSpeedProfile(ABC):
    def __init__(self, max_speed: float):
        self.max_speed: float = max_speed

    @abstractmethod
    def get_speed(self, time_elapsed: float | None = None, distance: float | None = None) -> float: ...
