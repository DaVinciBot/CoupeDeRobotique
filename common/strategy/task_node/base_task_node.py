from __future__ import annotations
import time
from typing import Optional, TYPE_CHECKING, Callable, List
from strategy.task import BaseTask, TaskStatus
from strategy.base_game_context import BaseGameContext

if TYPE_CHECKING:

    from strategy.transition import BaseTransition


class BaseTaskNode:
    """
    Noeud de graphe, encapsule un BaseTask + transitions + hooks + état,
    et fournit un handle() à appeler en boucle.
    """

    def __init__(
        self,
        name: str,
        task: BaseTask,
        score_func: Optional[Callable[[BaseTaskNode, BaseGameContext], float]] = None,
    ) -> None:
        self.name = name
        self.task = task
        self.transitions: List[BaseTransition] = []
        self.score_func = score_func or (lambda prev, ctx: 0.0)

        # --- état interne ---
        self.status: TaskStatus = TaskStatus.PENDING
        self.result: Optional[bool] = None
        self.exception: Optional[Exception] = None
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None

        # indicateurs pour on_enter / on_exit
        self._entered = False
        self._exited = False

    def add_transition(self, transition: BaseTransition) -> None:
        self.transitions.append(transition)

    def score(self, prev: BaseTaskNode, ctx: BaseGameContext) -> float:
        return self.score_func(prev, ctx)

    def on_enter(self, prev: Optional[BaseTaskNode], ctx: BaseGameContext) -> None:
        """Hook appelé une seule fois la première fois qu’on entre ici."""
        pass

    def on_exit(
        self, next_node: Optional[BaseTaskNode], ctx: BaseGameContext
    ) -> None:
        """Hook appelé une seule fois quand la tâche devient terminale."""
        pass

    def execute(self, ctx: BaseGameContext) -> bool:
        """
        Exécute ou poursuit la Task – ne fait QUE run().
        Retourne True si on est dans un état terminal.
        """
        # si déjà terminé
        if self.status in {TaskStatus.SUCCESS, TaskStatus.FAILURE, TaskStatus.TIMEOUT}:
            return True

        # premier appel
        if self.start_time is None:
            self.start_time = time.time()
            self.status = TaskStatus.IN_PROGRESS

        try:
            done = self.task.handle(ctx)
            self.result = done
            if done:
                self.status = TaskStatus.SUCCESS
                self.end_time = time.time()
            return done

        except TimeoutError as e:
            self.exception = e
            self.status = TaskStatus.TIMEOUT
            self.end_time = time.time()
            return True

        except Exception as e:
            self.exception = e
            self.status = TaskStatus.FAILURE
            self.end_time = time.time()
            return True

    def handle(self, ctx: BaseGameContext) -> bool:
        """
        À appeler en boucle :
          - init (on_enter) la première fois
          - appelle execute(ctx) à chaque tick
          - quand execute() retourne True, appelle on_exit() une seule fois
        Renvoie True si la tâche est finie (SUCCESS/FAILURE/TIMEOUT).
        """
        # 1) on_enter
        if not self._entered:
            self.on_enter(None, ctx)
            self._entered = True

        # 2) exécution
        done = self.execute(ctx)

        # 3) on_exit
        if done and not self._exited:
            self.on_exit(None, ctx)
            self._exited = True

        return done

    __call__ = handle  # permet node(ctx) comme raccourci
