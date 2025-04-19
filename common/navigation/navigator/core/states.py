from enum import Enum, auto

# TODO: garder que le state utile
class NavigatorState(Enum):
    IDLE = auto()  # Aucun déplacement en cours
    PLANNING = auto()  # Génération du chemin + trajectoire
    READY = auto()  # Prêt à bouger (trajectoire prête mais pas lancée)
    MOVING = auto()  # Exécution du mouvement en cours
    PAUSED = auto()  # Mouvement temporairement interrompu
    FINISHED = auto()  # Objectif atteint
    STOPPED = auto()  # Mouvement interrompu manuellement
    REPLANNING = auto()  # Recalcul du chemin/trajectoire
    ERROR = auto()  # Échec ou événement bloquant (obstacle, timeout...)

