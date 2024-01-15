import os
from .utils import Utils
from .api import update_log


class Logger:
    """
    Log dans un fichier (logs/YYYY-MM-DD.log) + sortie standard
    affiche dans le format YYYY-MM-DD HH:MM:SS | NIVEAU | message
    """

    def __init__(self):
        os.mkdir("logs") if not os.path.isdir("logs") else None
        date = Utils.get_current_date()["date"]
        self.log_file = f"{date.strftime('%Y-%m-%d')}.log"
        self.levels = ["INFO", "WARNING", "ERROR", "CRITICAL"]
        self.log_history = ""

    async def log(self, message: str, level: int = 0) -> None:
        """
        Log un message dans le fichier de log et dans la sortie standard

        :param message: message à logger
        :type message: str
        :param level: 0: INFO, 1: WARNING, 2: ERROR, 3: CRITICAL, defaults to 0
        :type level: int, optional
        """
        date_str = Utils.get_current_date()["date"]
        message = f"{date_str} | {self.levels[level]} | {message}"
        print(message)
        try:
            await update_log(message)
        except:
            pass
        with open(f"logs/{self.log_file}", "a") as f:
            f.write(message + "\n")
        self.log_history += message + "\n"
