# External imports
import asyncio
import random
from dataclasses import dataclass, field
from typing import List

# Import from common
from config_loader import CONFIG
from brain import Brain


from arena import ShowArena
from arena_zone import StuffZone


@dataclass
class Objective:
    task: Brain.task(process=False, run_on_start=False)  # objective type ("deploy_banner","build_floor_0",
    # "build_floor_1", "build_floor_2")
    name: str
    target_index: int = 0  # index of the target
    target_position: tuple[float, float] = (random.randint(0, 100), random.randint(0, 100))  # position of the target
    time_estimate: float = random.randint(0, 20)  # time estimate (won't try if it's too late)
    elevator_after: str = ""

    def __str__(self):
        r = f"{self.task}, at {self.target_index}, estimated time: {self.time_estimate}"
        match self.elevator_after:
            case "top":
                r += ", then raising elevator for next objective"
            case "bottom":
                r += ", then lowering elevator for next objective"
            case "intermediate":
                r += ", then setting elevator to intermediate position"
            case _:
                r += ", then nothing"
        return r

    @property
    def score(self) -> int:
        return getattr(CONFIG, self.name.upper(), 0)


@dataclass
class ObjectiveSupervisor:
    objectives: List[Objective] = field(default_factory=list)
    summary: dict = field(default_factory=lambda: {i: {} for i in range(11)}) # we keep a history of all the tasks
                                                                              # we launched and see which failed or not
    current_task = None
    task_finished = asyncio.Event()

    def add_objective(self, objective: Objective) -> None:
        # possibility to automatically compute target_index with target_position
        # see if it's worth it depending on the ram and rom of the rasp
        self.objectives.append(objective)
        self.summary[objective.target_index][objective.name] = False
        print(f"Adding new objective: {objective.name}")

    @staticmethod
    def calculate_time(time_estimate: float, target_position: tuple[float, float],
                       current_position: tuple[float, float]) -> float:
        # very simplified version to edit in the future
        distance = ((target_position[0] ** 2 - current_position[0] ** 2)
                    + (target_position[1] ** 2 - current_position[1] ** 2)) ** 0.5

        # speed in cm/s. hard coded value, to edit in the future
        speed = 50

        # not accurate at all, to edit in the future
        margin_error = speed * 0.1

        return distance / speed + time_estimate + margin_error

    # Looks if task has already been done and checks if the mandatory conditions are met before building
    # Ex : We build floor 0 before floor 1
    def is_interesting(self, task: str, target_index: int, arena: ShowArena) -> bool:
        if self.summary[target_index].get(task):
            print(f"Objective {task} not interesting")
            return False

        if any(isinstance(zone, StuffZone) and target_index == zone.index for zone in arena.zones):
            return False

        dependencies = {
            "deploy_banner": [],
            "build_floor_0": [],
            "build_floor_1": ["build_floor_0"],
            "build_floor_2": ["build_floor_0", "build_floor_1"],
        }

        for dependency in dependencies.get(task, []):
            if not self.summary[target_index].get(dependency):
                print(f"Objective {task} not interesting")
                return False

        return True

    def evaluate(self, start_time: float, arena: ShowArena) -> None:
        objective = self.objectives[0]

        timing = self.calculate_time(time_estimate=objective.time_estimate,
                                     target_position=objective.target_position,
                                     current_position=(0, 0))

        # à revoir, pour le 85 j'ai fait au pif.
        enough_time = timing + start_time < 85 and timing > 0

        if not enough_time:
            print("Task taking too long, we cancel")

        interesting = self.is_interesting(task=objective.name, target_index=objective.target_index,
                                          arena=arena)

        if not enough_time or not interesting:
            self.objectives.remove(objective)
            print(f"Objective {objective.name} cancelled")

    def prioritize(self) -> None:
        def sort_key(objective):
            # "banner" objective is always first
            if objective.name == "deploy_banner":
                return 0, 0
            # Sort by time_estimate, then sort by floor number (avoid to do floor2 before floor0 4ex)
            if objective.name.startswith("build_floor_"):
                floor_number = int(objective.name.split("_")[-1])  # Extract the floor number
                return 1, self.calculate_time(objective.time_estimate, objective.target_position,
                                              current_position=(0, 0)), floor_number
            # Default sorting for other objectives
            return 1, self.calculate_time(objective.time_estimate, objective.target_position,
                                          current_position=(0, 0)), float('inf')

        self.objectives.sort(key=sort_key)

    async def engage_new_tasks(self, start_time: float, arena: ShowArena) -> None:
        while self.objectives:
            self.prioritize()
            self.evaluate(start_time, arena)

            if not self.objectives:
                break
            current_objective = self.objectives[0]
            print(f"Starting objective: {current_objective.name}")

            self.current_task = asyncio.create_task(current_objective.task())

            try:
                res = (await self.current_task).result
                if res:
                    self.summary[current_objective.target_index][current_objective.name] = True
                    print(f"Objective complete: {current_objective.name}")
            except asyncio.CancelledError:
                print(f"Objective {current_objective.name} was cancelled.")
            finally:
                # Clean up after task finishes or is cancelled
                self.objectives.pop(0)
                self.current_task = None

        print("No more objectives")

    def cancel(self):
        if self.current_task:
            print(f"Cancelling {self.objectives[0].name} objective")
            self.current_task.cancel()