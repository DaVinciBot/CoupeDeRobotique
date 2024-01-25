from .Utils import Utils
from threading import Thread
from .State import is_logger_init, LOG_LEVEL, PRINT_LOG
from .API import update_log_sync
import os, types, functools


class Logger:
    """
    Log dans un fichier (logs/YYYY-MM-DD.log) + sortie standard
    affiche dans le format HH:MM:SS | NIVEAU | message
    """

    def __init__(self, func=None, *, level: int = 0):
        global is_logger_init
        """
        Logger init, ignore func and level param (for decorator)
        """
        # Decorator only
        if func is not None:
            self.func = func
            self.dec_level = level
            functools.update_wrapper(self, self.func)
            self.__code__ = self.func.__code__
        # Normal init
        os.mkdir("logs") if not os.path.isdir("logs") else None
        date = Utils.get_current_date()["date"]
        self.log_file = f"{date.strftime('%Y-%m-%d')}.log"
        self.levels = ["INFO", "WARNING", "ERROR", "CRITICAL", "NONE"]
        if not is_logger_init:
            self.log(f"Logger initialized, level: {self.levels[LOG_LEVEL]}")
            is_logger_init = True

    def log(self, message: str, level: int = 0) -> None:
        """
        Log un message dans le fichier de log et dans la sortie standard
        :param message: message à logger
        :type message: str
        :param level: 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, defaults to 0
        :type level: int, optional
        """
        if level < LOG_LEVEL or level > 3:
            return
        date_str = Utils.get_current_date()["date"].strftime("%H:%M:%S")
        message = f"{date_str} | {self.levels[level]} | {message}"
        if PRINT_LOG:
            print(message)
        with open(f"logs/{self.log_file}", "a") as f:
            f.write(message + "\n")
        try:
            Thread(target=update_log_sync, args=(message,)).start()
        except:
            pass

    def __call__(self, *args, **kwargs):
        """
        Décorateur, log l'appel de la fonction et ses paramètres
        """
        msg = f"{self.func.__qualname__.split('.')[0]} : {self.func.__name__}("
        # get positional parameters
        params = [
            f"{param}={value}"
            for param, value in zip(self.func.__code__.co_varnames, args)
        ]
        # get keyword parmeters
        params += [f"{key}={value}," for key, value in kwargs.items()]
        for e in params:
            if "self" in str(e):
                continue
            msg += str(e) + ", "
        self.log(msg[:-2] + ")", self.dec_level)
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        """
        Permet de faire un décorateur applicable à des méthodes
        """
        if obj is None:
            return self
        return types.MethodType(self, obj)