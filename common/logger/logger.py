# ====== Imports ======
# Standard library imports
import os
import types
import functools

from datetime import datetime

# Internal project imports
from logger.log_tools import (
    LogLevels,
    STYLES,
    center_and_limit,
    style,
    strip_ANSI,
)


# ====== Class Part ======
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
            print_log_level: LogLevels = LogLevels.INFO,
            file_log_level: LogLevels = LogLevels.DEBUG,
            print_log: bool = True,
            write_to_file: bool = True,
    ):
        """
        Logger init, ignore func and level param (for decorator)
        """

        self.identifier = identifier  # Overriden if Decorator

        # Decorator only
        if func is not None:
            self.func = func
            self.dec_level = decorator_level
            functools.update_wrapper(self, self.func)
            self.__code__ = self.func.__code__
            self.identifier = self.func.__qualname__.split(".")[0]

        # Normal init
        # Init attributes
        self.identifier_width = 12
        self.log_level_width = max([len(loglvl.name) for loglvl in LogLevels]) + 2
        self.print_log_level = print_log_level
        self.file_log_level = file_log_level
        self.print_log = print_log
        self.write_to_file = write_to_file

        os.mkdir("logs") if not os.path.isdir("logs") else None
        date = datetime.now()
        self.log_file = f"{date.strftime('%Y-%m-%d')}.log"

        if func is None:
            self.log(
                f"Logger initialized, "
                + f"print: {style(center_and_limit(self.print_log_level.name, self.log_level_width), STYLES.LogLevelsColorsDict[self.print_log_level]) if self.print_log else style(center_and_limit('NO', self.log_level_width), STYLES.RESET_ALL)}, "
                + f"write to file: {style(center_and_limit(self.file_log_level.name, self.log_level_width), STYLES.LogLevelsColorsDict[self.file_log_level]) if self.log_file else style(center_and_limit('NO', self.log_level_width), STYLES.RESET_ALL)}",
                level=LogLevels.INFO,
            )

    def message_factory(
            self,
            date_str: str,
            level: LogLevels,
            message: str,
            identifier_override: str | None = None,
    ) -> str:

        return (
                (style(date_str, STYLES.DATE))
                + " -> ["
                + (
                    style(
                        (
                            center_and_limit(self.identifier, self.identifier_width)
                            if identifier_override is None
                            else center_and_limit(
                                identifier_override, self.identifier_width
                            )
                        ),
                        STYLES.IDENTIFIER,
                    )
                )
                + "] "
                + (
                    style(
                        level.name.center(self.log_level_width),
                        STYLES.LogLevelsColorsDict[level],
                    )
                )
                + " | "
                + (style(message, STYLES.MESSAGE))
        )

    def log(
            self,
            message: str,
            level: LogLevels = LogLevels.WARNING,
            led_strip=None,
            identifier_override: str | None = None,
    ) -> None:
        """
        Log un message dans le fichier de log et dans la sortie standard
        :param message: message à logger
        :type message: str
        :param level: 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, defaults to 0
        :type level: int, optional
        """

        date_str = datetime.now().strftime("%H:%M:%S.%f")

        # Evaluate the str(message) value manually to make sure no weird operators happen
        message_str = self.message_factory(
            date_str=date_str,
            level=level,
            message=str(message),
            identifier_override=identifier_override,
        )

        if self.print_log and level >= self.print_log_level:
            print(message_str)

        if led_strip is not None:
            led_strip.log(level)

        if self.log_file and level >= self.file_log_level:
            with open(f"logs/{self.log_file}", "a") as f:
                f.write(
                    strip_ANSI(
                        message_str
                    )  # Remove ANSI escape sequences from the string to save to file, or it will not display properly no most interfaces (could keep them if displayed through cat for example)
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
        # get positional parameters
        params = [
            f"{param}={value}"
            for param, value in zip(self.func.__code__.co_varnames, args)
            if param != "self"
        ]
        # get keyword parmeters
        params += [f"{key}={value}" for key, value in kwargs.items()]
        msg = f"{self.func.__name__}(" + ", ".join(params) + ")"
        self.log(
            msg,
            self.dec_level,
        )
        return self.func(*args, **kwargs)

    def __get__(self, obj, objtype=None):
        """
        Permet de faire un décorateur applicable à des méthodes
        """
        if obj is None:
            return self
        return types.MethodType(self, obj)


class DummyLogger(Logger):
    def __init__(self, identifier="DummyLogger") -> None:
        super().__init__(
            identifier=identifier,
            decorator_level=LogLevels.DEBUG,
            print_log_level=LogLevels.INFO,
            file_log_level=LogLevels.FATAL,
            print_log=True,
            write_to_file=False,
        )
