from enum import Enum, auto


class NavigatorState(Enum):
    """Navigator state.

    Attributes:
        IDLE: No movement in progress.
        PLANNING: Path generation and trajectory planning.
        READY: Ready to move (trajectory ready but not started).
        MOVING: Execution of the movement in progress.
        PAUSED: Movement temporarily interrupted.
    """

    IDLE = auto()  # Aucun déplacement en cours
    PLANNING = auto()  # Génération du chemin + trajectoire
    READY = auto()  # Prêt à bouger (trajectoire prête mais pas lancée)
    MOVING = auto()  # Exécution du mouvement en cours
    PAUSED = auto()  # Mouvement temporairement interrompu
    FINISHED = auto()  # Objectif atteint
    STOPPED = auto()  # Mouvement interrompu manuellement
    REPLANNING = auto()  # Recalcul du chemin/trajectoire
    ERROR = auto()  # Échec ou événement bloquant (obstacle, timeout...)
