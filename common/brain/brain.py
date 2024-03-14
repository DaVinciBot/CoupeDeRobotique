from logger import Logger, LogLevels
import multiprocessing
import asyncio

from typing import TypeVar, Type, List, Callable, Coroutine
import inspect
from brain.stage import Stage
from time import sleep

TBrain = TypeVar("TBrain", bound="Brain")


class Brain:
    """
    The brain is a main controller of applications, a rasp can only handle one brain instance
    """

    def __init__(self, logger: Logger, child: TBrain) -> None:
        """
        This constructor have to be called in the __init__ method of the child class.
        By using super().__init__(logger, self)
        """
        if logger is None:
            raise ValueError("Logger is required for the brain to work properly.")
        self.logger = logger
        self.routines = []
        self.stages: list[Stage] = []
        child.dynamic_init()

    def dynamic_init(self):
        """
        This method is used to dynamically initialize the instance with the parameters of the caller.
        * You only have to call this method in the __init__ method of the child class.
        By Using super().__init__(logger, self)
        * The attributes of the child class will be initialized, based on the parameters of the caller.
        They will have the same name as the parameters of the child's __init__.
        """
        # Get the frame of the caller (the __init__ method of the child class)
        frame = inspect.currentframe().f_back.f_back
        # Get the params of the frame
        params = frame.f_locals

        # Assign the params to the instance
        for name, value in params.items():
            if name not in ["self", "logger"]:
                setattr(self, name, value)

    @classmethod
    def routine(cls, refresh_rate=1):
        """
        Decorator to add a routine function to the brain with a specified refresh rate in seconds.
        The routine is called in the main loop of the brain according to its refresh rate.
        :param refresh_rate: The refresh rate of the routine function.
        :return: The routine function.
        """

        def decorator(func: Callable[["Brain"], Coroutine[None, None, None]]):
            # Save the routine and its refresh rate as a tuple
            cls.routines.append((func, refresh_rate))
            return func

        return decorator

    async def make_routine(self, routine, refresh_rate) -> None:
        """
        This method wraps the routine in a loop and calls it according to the refresh rate.
        * It also handles the exceptions and logs them
        :param routine: The routine to be called in the main loop
        :param refresh_rate: The refresh rate of the routine
        :return: None
        """
        self.logger.log(
            f"Brain [{self}], routine [{routine.__name__}] started", LogLevels.INFO
        )
        while True:
            try:
                await routine(self)
            except Exception as error:
                self.logger.log(
                    f"Brain [{self}]-[{routine.__name__}] error: {error}",
                    LogLevels.ERROR,
                )
            await asyncio.sleep(refresh_rate)

    def get_routines(self) -> List[Callable[[], Coroutine[None, None, None]]]:
        """
        This method return a list of the brain's routines. They have to be added to
        the background tasks of the main loop.
        """
        return [
            lambda routine=routine, refresh_rate=rate: self.make_routine(
                routine, refresh_rate
            )
            for routine, rate in self.routines
        ]

    @classmethod
    def stage(cls, stime):
        def decorator(func):
            cls.stages.append(Stage(func, len(cls.stages), stime))
            return func

        return decorator

    def make_stage(self, stage) -> None:
        """
        This method wraps the routine in an infinite call loop.
        * It also handles the exceptions and logs them
        :param stage: Stage's function
        :return: None
        """
        self.logger.log(
            f"Brain [{self}], stage [{stage.__name__}] started", LogLevels.INFO
        )
        try:
            stage(self)
        except Exception as error:
            self.logger.log(
                f"Brain [{self}]-[{stage.__name__}] error: {error}",
                LogLevels.ERROR,
            )

    def run_stage(self)->None: # devrait être défini comme une routine pour être exécutée en // mais conflit avec le type du décorateur, décorer la dernière fonction avec un etime
        """executes stages one after the other according to the time given into the decorators 
        """
        if len(self.stages) > 0:
            self.stages.sort(key=lambda x: x.stime)
            current_process = None
            sleep(self.stages[0].stime)
            for i in range(len(self.stages) - 1):
                current_process = multiprocessing.Process(
                    target=self.make_stage, args=(self.stages[i].func,)
                )
                current_process.start()
                if (self.stages[i].etime != -1) and self.stages[
                    i + 1
                ].stime > self.stages[i].etime:
                    sleep(self.stages[i].etime - self.stages[i].stime)
                    current_process.terminate()
                    current_process.join()
                    sleep(self.stages[i + 1].stime - self.stages[i].etime)
                else:
                    sleep(self.stages[i + 1].stime - self.stages[i].stime)
                    current_process.terminate()
                    current_process.join()
            current_process = multiprocessing.Process(
                target=self.make_stage, args=(self.stages[-1].func,)
            )
            current_process.start()
            if self.stages[-1].etime != -1:
                sleep(self.stages[-1].etime)
                current_process.terminate()
                current_process.join()
    
    def log_stage(self,stage)->None:
        """not used for the moment

        Args:
            stage (_type_): the stage to log
        """
        string = ""
        for nom_parametre, valeur_parametre in stage.__dict__.items():
            if callable(valeur_parametre):
                string+=f"{nom_parametre}: {valeur_parametre.__name__} ,"
            else:
                string+=f"{nom_parametre}: {valeur_parametre} ,"
        self.logger.log(f"Brain [{self}], stage [{string[:-1]}] added", LogLevels.INFO)   

    def __str__(self) -> str:
        return self.__class__.__name__
