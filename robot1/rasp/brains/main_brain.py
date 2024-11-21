# External imports
import asyncio
import random
import time
import math
from dataclasses import dataclass, field
from typing import List

# Import from common
from config_loader import CONFIG
from brain import Brain

from WS_comms import WSmsg, WSclientRouteManager, WServerRouteManager
from geometry import OrientedPoint, Point, distance, Polygon
from arena import MarsArena, Plants_zone
from logger import Logger, LogLevels
# from led_strip import LEDStrip
from utils import Utils
# from GPIO import PIN

# Import from local path
from utils import LidarMode, AntiCollisionHandle, GoToResult
# from controllers import RollingBasis, Actuators
from sensors import Lidar


"""

Tasks : 
- build floor 0
- build floor 1
- build floor 2
- deploy banner


Objective class :
- __str__ : describes the state of the elevator
- add_objective : adding a task to do
- calculate_time (static) : return the time it takes to go to the position of the task and realizing it
- is_interesting (static) : return if rob should do the task according the state of the Arena
- evaluate : checks if every task is doable and deletes the impossible ones
- prioritize : sorts the list of objectives by priority (points then time)
- next_objective : return the next doable objective or None

list de Task à la place de faire un dict

Classe task parent :
- run (async to add a timeout)
- interrupt

Creer classes qui héritent de task:
- floor0
- floor1
- floor2
- deploy



"""


@dataclass
class Objective:
    objectives: List[dict] = field(default_factory=list)

    def __str__(self):
        r = "\n"
        for objective in self.objectives:
            r += f"{objective['task']}, at {objective['target_index']}, estimated time: {objective['time_estimate']}"
            match objective['elevator_after']:
                case "top":
                    r += ", then raising elevator for next objective"
                case "bottom":
                    r += ", then lowering elevator for next objective"
                case "intermediate":
                    r += ", then setting elevator to intermediate position"
                case _:
                    r += ", then nothing"

            r += "\n"
        return r

    def add_objective(self, task: str, target_position: tuple[float, float], target_index: int,
                      elevator_after: str = "") -> None:
        # possibility to automatically compute target_index with target_position
        # see if it's worth it depending on the ram and rom of the rasp
        self.objectives.append(
            {
                "task": task,
                "target_position": target_position,
                "target_index": target_index,
                "elevator_after": elevator_after,
                "score": getattr(CONFIG, task.upper(), 0),
                "time_estimate": random.randint(0, 30),  # to edit
            }
        )

    @staticmethod
    def calculate_time(time_estimate: float, target_position: tuple[float, float],
                       current_position: tuple[float, float]) -> float:
        # very simplified version to edit in the future
        distance = ((target_position[0]**2 - current_position[0]**2)
                    + (target_position[1]**2 - current_position[1]**2))**0.5

        # speed in cm/s. hard coded value, to edit in the future
        speed = 50

        # not accurate at all, to edit in the future
        margin_error = speed * 0.1

        return distance/speed + time_estimate + margin_error

    @staticmethod
    def is_interesting(task: str, target_index: int, arena) -> bool:
        return not ( False
                # (task == "banner")
                # or arena.pickup_zones[target_index].visited
        )

    def evaluate(self, start_time: float, arena: MarsArena) -> None:
        for objective in self.objectives:
            timing = self.calculate_time(time_estimate=objective["time_estimate"],
                                         target_position=objective["target_position"],
                                         current_position=(0, 0))

            enough_time = timing + start_time < 30 and timing > 0

            interesting = self.is_interesting(task=objective["task"], target_index=objective["target_index"],
                                              arena=arena)

            if not enough_time or not interesting:
                self.objectives.remove(objective)

    def prioritize(self) -> None:
        # primitive sorting method to review later
        self.objectives.sort(key=lambda objective: (-objective["score"], objective["time_estimate"]))

    def next_objective(self) -> dict:
        return self.objectives.pop(0) if self.objectives else None





@dataclass
class Objective2:
    task: str  # objective type ("pickup","drop_to_zone","drop_to_gardener")
    target_index: int  # index of the target
    target_position: tuple[float, float]  # position of the target
    time_estimate: float = -1.0  # time estimate (won't try if it's too late)
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
        return getattr(CONFIG, self.task.upper(), 0)

    def enough_time(self, start_time) -> bool:

        if (
                Utils.get_ts() + self.time_estimate - start_time > 80
                and self.time_estimate > 0
        ):
            return False
        return True

    def is_interesting(self, arena) -> bool:
        return not ( False
            # (task == "banner")
            # or arena.pickup_zones[target_index].visited
        )

    def evaluate(self, start_time, arena) -> bool:
        return self.enough_time(start_time) and self.is_interesting(arena)


@dataclass
class Objective2Manager:
    objectives: List[Objective2] = field(default_factory=list)

    def add_objective(self, objective: Objective2) -> None:
        # possibility to automatically compute target_index with target_position
        # see if it's worth it depending on the ram and rom of the rasp
        self.objectives.append(objective)

    @staticmethod
    def calculate_time(time_estimate: float, target_position: tuple[float, float],
                       current_position: tuple[float, float]) -> float:
        # very simplified version to edit in the future
        distance = ((target_position[0]**2 - current_position[0]**2)
                    + (target_position[1]**2 - current_position[1]**2))**0.5

        # speed in cm/s. hard coded value, to edit in the future
        speed = 50

        # not accurate at all, to edit in the future
        margin_error = speed * 0.1

        return distance/speed + time_estimate + margin_error

    @staticmethod
    def is_interesting(task: str, target_index: int, arena) -> bool:
        return not ( False
                # (task == "banner")
                # or arena.pickup_zones[target_index].visited
        )

    def evaluate(self, start_time: float, arena: MarsArena) -> None:
        for objective in self.objectives:
            timing = self.calculate_time(time_estimate=objective.time_estimate,
                                         target_position=objective.target_position,
                                         current_position=(0, 0))

            enough_time = timing + start_time < 30 and timing > 0

            interesting = self.is_interesting(task=objective.task, target_index=objective.target_index,
                                              arena=arena)

            if not enough_time or not interesting:
                self.objectives.remove(objective)

    def prioritize(self) -> None:
        # primitive sorting method to review later
        self.objectives.sort(key=lambda objective: (-objective.score, objective.time_estimate))

    def next_objective(self) -> Objective2:
        return self.objectives.pop(0) if self.objectives else None


class MainBrain(Brain):
    """
    This brain is the main controller of ROB (robot1).
    """

    # Controllers functions
    # from brains.controllers_brain import ()

    # Sensors functions
    # from brains.sensors_brain import ()

    # Com functions
    # from brains.com_brain import zombie_mode

    # Init the brain
    def __init__(
            self,
            logger: Logger,
    ) -> None:
        # Save this for later use (when re-creating the arena)
        self.logger_arena: Logger
        self.start_time = -1

        # Init the brain
        super().__init__(logger, self)



        self.logger.log(
            f"Mode: {'zombie' if CONFIG.ZOMBIE_MODE else 'game'}", LogLevels.INFO
        )

    """
        Tasks
    """
    """
    @Brain.task(process=False, run_on_start=True, refresh_rate=1)
    async def coucou(self):
        self.logger.log("Coucou Anne-Marie", LogLevels.INFO)

    @Brain.task(process=True, run_on_start=True, refresh_rate=1)
    def coucou(self):
        self.logger.log("Yo je suis dans un autre process carrément", LogLevels.INFO)

    @Brain.task(process=False, run_on_start=False)
    async def methode_one_shot(self):
        self.logger.log("je tente un one shot", LogLevels.INFO)

    # Method to calculate what is the best next task based on time and points
    @Brain.task(process=False, run_on_start=True, refresh_rate=1)
    async def next_best_objective(self) -> str:
        objectives: list[Objective2] = [
            Objective2(task="build_floor_0", target_index=1, time_estimate=10, elevator_after="top"),
            Objective2(task="build_floor_1", target_index=1, time_estimate=10, elevator_after="top"),
            Objective2(task="build_floor_2", target_index=1, time_estimate=10, elevator_after="top"),
            Objective2(task="deploy_banner", target_index=1, time_estimate=10, elevator_after="top")]

        best_objective: str = None
        max_value = 0
        Arena: MarsArena

        for objective in objectives:
            if objective.score / await self.estimate_time(objective) > max_value and objective.evaluate(start_time=1,
                                                                                                        arena=Arena):
                best_objective = objective.task
                max_value = objective.score/await self.estimate_time(objective)

        return best_objective
    
    async def estimate_time(self, task: Objective2) -> float:
        # calcul du temps que ça prend pour aller à la task
        robot_speed = CONFIG.ROBOT_SPEED  # existe pas encore
        # calcul distance
        distance = task.target_index
        time_to_go_to = distance / robot_speed
        return time_to_go_to + task.time_estimate
    """

    @Brain.task(process=True, run_on_start=True, refresh_rate=1, define_loop_later=True)
    def test(self):
        arena = None

        big_guy = Objective()

        big_guy.add_objective("deploy_banner", (100, 200), 5, "top")
        big_guy.add_objective("build_floor_0", (0, 50), 2, "intermediate")
        big_guy.add_objective("build_floor_1", (0, 50), 2, "top")
        big_guy.add_objective("build_floor_2", (0, 50), 2, "bottom")
        big_guy.add_objective("build_floor_0", (15, 0), 4, "intermediate")
        big_guy.add_objective("build_floor_1", (15, 0), 4, "bottom")
        big_guy.add_objective("build_floor_0", (200, 600), 11, "bottom")
        self.start_time = time.time()
        big_guy.prioritize()

        # ---Loop--- #
        self.logger.log(big_guy.__str__(), LogLevels.INFO)
        self.logger.log(time.time() - self.start_time, LogLevels.INFO)
        big_guy.evaluate(time.time() - self.start_time, arena)
        # big_guy.next_objective()






