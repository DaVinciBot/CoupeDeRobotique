# External imports
import asyncio
import random
import time
import math
from dataclasses import dataclass, field
from typing import List, Dict

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
    def is_interesting(self, task: str, target_index: int, arena) -> bool:
        if self.summary[target_index].get(task):
            print(f"Objective {task} not interesting")
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

    def evaluate(self, start_time: float, arena: MarsArena) -> None:
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

    async def engage_new_tasks(self, start_time: float, arena: MarsArena) -> None:
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
    """

    # Method to calculate what is the best next task based on time and points
    @Brain.task(process=False, run_on_start=False)
    async def build_floor_0(self) -> bool:
        try:
            self.logger.log("Boom! Je récupère les cannettes.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Je m'occuppe des planches.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Et voilà étage 0 construit !", LogLevels.INFO)
            await asyncio.sleep(1)
            return True
        except Exception as e:
            self.logger.log(f"Erreur lors de la construction de l'étage 0: {e}", LogLevels.ERROR)
            self.logger.log(f"Passage à la tache suivante", LogLevels.ERROR)
            return False

    @Brain.task(process=False, run_on_start=False)
    async def build_floor_1(self) -> bool:
        try:
            self.logger.log("Boom! Je récupère les autres cannettes.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Je m'occuppe de la planche.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("L'ascenceur monte et descend.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Et voilà étage 1 construit !", LogLevels.INFO)
            return True
        except Exception as e:
            self.logger.log(f"Erreur lors de la construction de l'étage 1: {e}", LogLevels.ERROR)
            self.logger.log(f"Passage à la tache suivante", LogLevels.ERROR)
            return False

    @Brain.task(process=False, run_on_start=False)
    async def build_floor_2(self) -> bool:
        try:
            self.logger.log("Boom! Je récupère des cannettes à un autre endroit carrément.", LogLevels.INFO)
            await asyncio.sleep(1)
            # Erreur faite exprès pour tester comment le code régit si la fonction crash
            zesrty-èu_io
            self.logger.log("Je m'occuppe d'une nouvelle planche encore.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("L'ascenceur monte et descend et remonte et redescend.", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Et voilà étage 2 construit !", LogLevels.INFO)
            return True
        except Exception as e:
            self.logger.log(f"Erreur lors de la construction de l'étage 2: {e}", LogLevels.ERROR)
            self.logger.log(f"Passage à la tache suivante", LogLevels.ERROR)
            return False

    @Brain.task(process=False, run_on_start=False)
    async def deploy_banner(self) -> bool:
        try:
            self.logger.log("Déploiement en cours...", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Boom, +20 points", LogLevels.INFO)
            await asyncio.sleep(1)
            self.logger.log("Banière déployée !", LogLevels.INFO)
            return True
        except Exception as e:
            self.logger.log(f"Erreur lors du déploiement: {e}", LogLevels.ERROR)
            self.logger.log(f"Passage à la tache suivante", LogLevels.ERROR)
            return False

    @Brain.task(process=False, run_on_start=True)
    async def launch(self):
        self.start_time = time.time()
        objectives = [
            Objective(task=self.build_floor_1, name="build_floor_1", target_index=0, target_position=(20, 20)),
            Objective(task=self.build_floor_0, name="build_floor_0", target_index=0, target_position=(20, 20)),
            Objective(task=self.build_floor_2, name="build_floor_2", target_index=0, target_position=(20, 20)),
            Objective(task=self.build_floor_0, name="build_floor_1", target_index=1, target_position=(10, 15)),
            Objective(task=self.build_floor_0, name="build_floor_0", target_index=2, target_position=(0, 0)),
            Objective(task=self.deploy_banner, name="deploy_banner", target_index=4)
        ]

        obs = ObjectiveSupervisor()

        for o in objectives:
            obs.add_objective(o)

        asyncio.create_task(obs.engage_new_tasks(time.time()-self.start_time, arena=None))
        await asyncio.sleep(2)
        obs.cancel()

        # add new objective
        obs.add_objective(
            Objective(task=self.build_floor_0, name="build_floor_0", target_index=3, target_position=(10, 10)))

        # start building floor0 cancel it then try to build floor1 at same index
        obs.add_objective(
            Objective(task=self.build_floor_0, name="build_floor_0", target_index=5, target_position=(30, 30)))
        obs.add_objective(
            Objective(task=self.build_floor_0, name="build_floor_1", target_index=5, target_position=(30, 30)))

        await asyncio.sleep(18)
        obs.cancel()








