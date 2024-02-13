import multiprocessing
import time
from bot import State
from typing import Dict, Callable
from bot.actions import *

def time_manager(running_time, instruction_queue):
    """this function manage time 

    Args:
        running_time (_type_): _description_
        stop_signal (_type_): _description_
    """
    start_time = time.time()
    solar_panel_flag = False
    plant_flag = False

    while running_time.value <= State.time_to_return_home:
        if not solar_panel_flag and running_time.value >= State.solar_panel_time:
            instruction_queue.put("SOLAR PANEL")
            solar_panel_flag = True

        elif not plant_flag and running_time.value >= State.plant_time:
            instruction_queue.put("PLANT")
            plant_flag = True

        elapsed_time = time.time() - start_time
        running_time.value = round(elapsed_time, 2)

    instruction_queue.put("RETURN HOME")

def action_manager(actions:Dict[str, Callable[[], None]],running_time, instruction_queue):
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
            current_process = multiprocessing.Process(target=actions.get(action, unknown_action))
            current_process.start()
            
            print(f"Launched {action} at {running_time.value}")

            if action == "RETURN HOME":
                break
            
        time.sleep(1)

def main():
    # Créez une valeur partagée pour le temps
    running_time = multiprocessing.Value('d', 0)

    # Créez une queue partagée pour les instructions
    instruction_queue = multiprocessing.Queue()
    
    # Créer la liste des actions à réaliser
    actions : Dict[str, Callable[[], None]] = {"PLANT":plant,"SOLAR PANEL":solar_panel,"RETURN HOME":return_home}

    # Créez deux processus pour exécuter time_manager et action_manager
    timer_process = multiprocessing.Process(target=time_manager, args=(running_time, instruction_queue))
    action_process = multiprocessing.Process(target=action_manager, args = (actions,running_time,instruction_queue))

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

if __name__ == '__main__':
    main()