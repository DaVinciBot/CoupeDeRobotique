class TaskPlannerSolution:
    def __init__(self, ordered_tasks, score, duration):
        self.ordered_tasks = ordered_tasks
        self.score = score
        self.duration = duration

    def __str__(self):
        return (
            f"TaskPlannerSolution with score {self.score} and duration {self.duration}"
        )
