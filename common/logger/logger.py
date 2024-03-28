from utils.utils import Utils
from logger.log_tools import LogLevels, STYLES, center_and_limit, style


import os, types, functools


class Logger:
    """
    Log dans un fichier (logs/YYYY-MM-DD.log) + sortie standard
    affiche dans le format HH:MM:SS | NIVEAU | message
    """

    def __init__(
        self,
        func=None,
        *,
        identifier: str = "unknown",
        decorator_level: LogLevels = LogLevels.DEBUG,
        print_log_level: LogLevels = LogLevels.DEBUG,
        file_log_level: LogLevels = LogLevels.DEBUG,
        print_log: bool = True,
        write_to_file: bool = True,
    ):
        """
        Logger init, ignore func and level param (for decorator)
        """
        # Decorator only
        if func is not None:
            self.func = func
            self.dec_level = decorator_level
            functools.update_wrapper(self, self.func)
            self.__code__ = self.func.__code__

        # Normal init
        # Init attributes
        identifier_width = 12
        self.log_level_width = max([len(loglvl.name) for loglvl in LogLevels]) + 2
        self.identifier = identifier
        self.identifier_str = center_and_limit(self.identifier, identifier_width)
        self.print_log_level = print_log_level
        self.file_log_level = file_log_level
        self.print_log = print_log
        self.write_to_file = write_to_file

        os.mkdir("logs") if not os.path.isdir("logs") else None
        date = Utils.get_date()
        self.log_file = f"{date.strftime('%Y-%m-%d')}.log"

        self.log(
            f"Logger initialized, "
            + f"print: {center_and_limit(self.print_log_level.name if self.print_log else 'NO', self.log_level_width)}, "
            + f"write to file: {center_and_limit(self.file_log_level.name if self.log_file else 'NO', self.log_level_width)}",
            level=LogLevels.INFO,
        )

    def message_factory(
        self, date_str: str, level: LogLevels, message: str, styles: bool = False
    ) -> str:

        return (
            (style(date_str, STYLES.DATE if styles else ""))
            + " -> ["
            + (style(self.identifier_str, STYLES.IDENTIFIER if styles else ""))
            + "] "
            + (
                style(
                    level.name.center(self.log_level_width),
                    STYLES.LogLevelsColorsDict[level] if styles else "",
                )
            )
            + " | "
            + (style(message, STYLES.MESSAGE if styles else ""))
        )

    def log(self, message: str, level: LogLevels = LogLevels.WARNING) -> None:
        """
        Log un message dans le fichier de log et dans la sortie standard
        :param message: message à logger
        :type message: str
        :param level: 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, defaults to 0
        :type level: int, optional
        """
        # Evaluate the str value now to make sure no weird operators happen
        message_str = str(message)
        date_str = Utils.get_str_date()

        if self.print_log and level >= self.print_log_level:
            print(
                self.message_factory(
                    date_str=date_str, level=level, message=message_str, styles=True
                )
            )

        if self.log_file and level >= self.file_log_level:
            with open(f"logs/{self.log_file}", "a") as f:
                f.write(
                    self.message_factory(
                        date_str=date_str,
                        level=level,
                        message=message_str,
                        styles=False,
                    )
                    + "\n"
                )

        # Sync logs to server (deprecated for now)
        # try:
        #     Thread(target=update_log_sync, args=(message,)).start()
        # except:
        #     pass

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
