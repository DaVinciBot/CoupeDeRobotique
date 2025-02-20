class Task:
    _id_counter = 1

    from typing import Callable, Optional

    def __init__(
        self,
        action_func: Callable,
        start_func: Optional[Callable] = None,
        execution_time: Optional[float] = 0,
        name: Optional[str] = None,
        score: Optional[float] = 0,
    ):
        self.id = Task._id_counter
        Task._id_counter += 1
        self.action_func = action_func
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
