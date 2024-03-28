from utils.utils import Utils
from logger.log_tools import LogLevels, STYLES


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
        dec_level: LogLevels = LogLevels.DEBUG,
        log_level: LogLevels = LogLevels.DEBUG,
        print_log: bool = True,
        write_to_file: bool = True,
    ):
        """
        Logger init, ignore func and level param (for decorator)
        """
        # Decorator only
        if func is not None:
            self.func = func
            self.dec_level = dec_level
            functools.update_wrapper(self, self.func)
            self.__code__ = self.func.__code__

        # Normal init
        # Init attributes
        identifier_width = 12
        self.log_level_width = max([len(loglvl.name) for loglvl in LogLevels]) + 2
        self.identifier = identifier
        self.identifier_str = (
            (self.identifier[: identifier_width - 2] + "..")
            if len(self.identifier) > identifier_width
            else self.identifier.center(identifier_width)
        )
        self.log_level = log_level
        self.print_log = print_log
        self.write_to_file = write_to_file

        os.mkdir("logs") if not os.path.isdir("logs") else None
        date = Utils.get_date()
        self.log_file = f"{date.strftime('%Y-%m-%d')}.log"

        self.log(
            f"Logger initialized [{self.identifier}], level: {self.log_level.name}"
        )

    def message_factory(
        self, date_str: str, level: LogLevels, message: str, colors: bool = False
    ) -> str:

        def frame(content: str, style: str) -> str:
            if colors:
                content = style + content + STYLES.RESET_ALL
            return content

        return (
            frame(date_str, STYLES.DATE)
            + " -> ["
            + frame(self.identifier_str, STYLES.IDENTIFIER)
            + "] "
            + frame(
                level.name.center(self.log_level_width),
                STYLES.LogLevelsColorsDict[level],
            )
            + " | "
            + frame(message, STYLES.MESSAGE)
        )

    def log(self, message: str, level: LogLevels = LogLevels.WARNING) -> None:
        """
        Log un message dans le fichier de log et dans la sortie standard
        :param message: message à logger
        :type message: str
        :param level: 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, defaults to 0
        :type level: int, optional
        """
        if level >= self.log_level:
            # Evaluate the str value now to make sure no weird operators happen
            message_str = str(message)
            date_str = Utils.get_str_date()

            if self.print_log:
                print(
                    self.message_factory(
                        date_str=date_str, level=level, message=message_str, colors=True
                    )
                )

            if self.log_file:
                with open(f"logs/{self.log_file}", "a") as f:
                    f.write(
                        self.message_factory(
                            date_str=date_str,
                            level=level,
                            message=message_str,
                            colors=False,
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
