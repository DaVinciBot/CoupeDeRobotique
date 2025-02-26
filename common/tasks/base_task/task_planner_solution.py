import json


class TaskPlannerSolution:
    def __init__(self, ordered_tasks, score, duration):
        self.ordered_tasks = ordered_tasks
        self.score = score
        self.duration = duration

    def __str__(self):
        return (
            f"TaskPlannerSolution with score {self.score} and duration {self.duration}s"
        )

    @staticmethod
    def load_solution(file_path: str):
        with open(file_path, "r") as f:
            data = json.load(f)
            return TaskPlannerSolution(
                ordered_tasks=data["route"],
                score=data["score"],
                duration=data["duration"],
            )
