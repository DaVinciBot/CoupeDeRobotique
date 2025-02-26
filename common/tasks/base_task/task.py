from arena import BaseArena, BaseArenaZone
from geometry import Point, OrientedPoint, Polygon
from movement import GoToParams


class Task:
    _id_counter = 1

    from typing import Callable, Optional

    def __init__(
        self,
        action_func: Callable,
        position: Point | OrientedPoint | BaseArenaZone | Polygon,
        go_to_params: GoToParams = None,  # TODO: transform to trajectory_params that don't include destination wich is computed dynamicaly
        start_func: Optional[Callable] = None,
        execution_time: Optional[float] = 0,
        name: Optional[str] = None,
        score: Optional[float] = 0,
    ):
        self.id = Task._id_counter
        Task._id_counter += 1
        self.action_func = action_func
        self.position = position
        self.go_to_params = go_to_params
        self.start_func = start_func
        self.execution_time = execution_time
        self.name = name
        self.score = score

    def start(self):
        if self.start_func:
            self.start_func()

    def execute(self):
        self.action_func()

    def __str__(self):
        return f"Task {self.id} {": " + self.name if self.name else ""}, execution_time: {self.execution_time}, score: {self.score}"

    @staticmethod
    def reset_id_counter():
        Task._id_counter = 1
