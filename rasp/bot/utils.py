from datetime import datetime
from multiprocessing import Process, Queue
from api import API
import json
import os

def run_api(queue: Queue):
    obj = queue.get()
    a = API(obj)
    a.run()

class State:
    """
    Classe permettant de gérer l'état du robot
    """
    def __init__(self, state: dict, file: str = "state.json") -> None:
        self.state = state
        self.lidar_data = []
        self.file = file
        
    def get(self, key: str) -> str:
        """
        Permet de récupérer une valeur de l'état

        :param key: une clé de l'état
        :type key: str
        :return: la valeur de la l'état correspondant à la clé
        :rtype: str
        """
        return self.state[key]
    
    def set(self, key: str, value: str) -> None:
        """
        Permet de modifier l'état

        :param key: la clé de l'état à modifier
        :type key: str
        :param value: la valeur à modifier
        :type value: str
        """
        self.state[key] = value
        with open(self.file, "w") as f:
            json.dump(self.state, f)
            
    def delete(self, key: str) -> None:
        """
        supprime un couple clé/valeur de l'état

        :param key: la clé du couple à supprimer
        :type key: str
        """
        del self.state[key]
        with open(self.file, "w") as f:
            json.dump(self.state, f)
            
    def get_all(self) -> dict:
        """
        retourne l'état complet

        :return: l'état complet
        :rtype: dict
        """
        return self.state
    
    
class Utils:
    def get_current_date() -> dict:
        """
        Récupère la date actuelle et son timestamp

        :return: date actuelle (datetime obj) et timestamp (int)
        :rtype: dict
        """
        now = datetime.now()
        timestamp = datetime.timestamp(now)
        return {"date": now, "date_timespamp": timestamp}

    def start_api() -> None:
        """
        Lance l'API dans un processus séparé
        """
        queue = Queue()
        p = Process(target=run_api, args=(queue,))
        p.start()

    def load_state() -> State:
        """
        Charge l'état du serveur depuis le fichier state.json
        """
        if not (os.path.isdir("state.json") or os.path.exists("state.json")):
            with open("state.json", "w") as f:
                json.dump({}, f)
        with open("state.json", "r") as f:
            return State(json.load(f))
        
    
            