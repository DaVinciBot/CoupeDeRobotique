
import multiprocessing
import time
from bot import State
from typing import Dict, Callable
from bot.Logger import Logger

class Game():
    def __init__(self) -> None:
        # set to 0 to avoid errors
        self.start_time = 0
        self.game_finished = False
        self.go_to_verif = False # when true trajectory is checked to avoid forbidden moves
        self.activate_lidar = True # when true stops when an obstacle is detected
        
        # starting times, time is a delta from the start_time
        self.plant_time = 0
        self.solar_panel_time = 5
        self.return_home_time = 7
        self.l = Logger()

    def time_manager(self,running_time, instruction_queue):
        """this function manage time 

        Args:
            running_time (_type_): _description_
            stop_signal (_type_): _description_
        """
        start_time = time.time()
        solar_panel_flag = False
        plant_flag = False

        while running_time.value <= self.return_home_time:
            if not solar_panel_flag and running_time.value >= self.solar_panel_time:
                instruction_queue.put("SOLAR PANEL")
                solar_panel_flag = True

            elif not plant_flag and running_time.value >= self.plant_time:
                instruction_queue.put("PLANT")
                plant_flag = True

            elapsed_time = time.time() - start_time
            running_time.value = round(elapsed_time, 2)

        instruction_queue.put("RETURN HOME")

    def action_manager(self, actions:Dict[str, Callable[[], None]],running_time, instruction_queue):
        # Exécute la fonction action
        current_process = None
        while True:
            # Vérifie si une action a été reçue
            if not instruction_queue.empty():
                action = instruction_queue.get()
                
                # Arrête le processus existant
                if isinstance(current_process, multiprocessing.Process) and current_process.is_alive():
                    current_process.terminate()
                    current_process.join()  # Attendez que le processus existant se termine

                # Crée un nouveau processus pour l'action en cours
                current_process = multiprocessing.Process(target=actions.get(action, self.unknown_action))
                current_process.start()
                
                print(f"Launched {action} at {running_time.value}")

                if action == "RETURN HOME":
                    break
                
            time.sleep(1)

    def main(self):
        # Créez une valeur partagée pour le temps
        running_time = multiprocessing.Value('d', 0)

        # Créez une queue partagée pour les instructions
        instruction_queue = multiprocessing.Queue()
        
        # Créer la liste des actions à réaliser
        actions : Dict[str, Callable[[], None]] = {"PLANT":self.plant,"SOLAR PANEL":self.solar_panel,"RETURN HOME":self.return_home}

        # Créez deux processus pour exécuter time_manager et action_manager
        timer_process = multiprocessing.Process(target=self.time_manager, args=(running_time, instruction_queue))
        action_process = multiprocessing.Process(target=self.action_manager, args = (actions,running_time,instruction_queue))

        # Démarrez les processus
        timer_process.start()
        action_process.start()

        try:
            # Attendez que les processus se terminent
            timer_process.join()
            action_process.join()
        except KeyboardInterrupt:
            # Si l'utilisateur interrompt manuellement le programme, terminez proprement les processus
            print("Interruption manuelle. Arrêt des processus.")
            timer_process.terminate()
            action_process.terminate()
            timer_process.join()
            action_process.join()

        print("Programme principal terminé.")
        
    def unknown_action(self):
        print("received an unknown action")

    def plant(self):
        print("début de la phase plante")
        for i in range(20):
            self.l.log(i)
            time.sleep(1)
        
    def solar_panel(self):
        print("début de la phase panneau solaire")
        
    def return_home(self):
        print("return home")
        
    # def go_to(self, __object : object,  distance = 0, nb_digits : int = 2, closer = True)->bool:
    #     destination_point = compute_go_to_destination(self.rolling_basis.odometrie,__object,distance,nb_digits=nb_digits,closer=closer)
    #     if isinstance(destination_point,OrientedPoint):
    #         if State.go_to_verif:
    #             if self.arena.enable_go_to(self.rolling_basis.odometrie,destination_point):
    #                 self.rolling_basis.Go_ToPoint(destination_point)
    #                 return True
    #             return False
    #         self.rolling_basis.Go_ToPoint(destination_point)
    #         return True
    #     return False