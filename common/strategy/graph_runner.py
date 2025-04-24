from typing import List, Optional, Dict
from strategy.base_game_context import BaseGameContext
from strategy.task_node import BaseTaskNode
from strategy.transition import BaseTransition


class GraphRunner:
    def __init__(self, start: BaseTaskNode, parallel: bool = False) -> None:
        self.parallel = parallel

        # liste des nœuds actuellement en cours
        self.active: List[BaseTaskNode] = [start]
        # on pourra garder la trace du prédécesseur si besoin
        self.prev: Dict[BaseTaskNode, Optional[BaseTaskNode]] = {start: None}

    def handle(self, ctx: BaseGameContext) -> None:
        """
        À appeler en boucle :
        - chaque nœud actif reçoit son handle(ctx)
        - quand handle renvoie True, on tyre les transitions
        - on calcule la nouvelle liste active
        """
        next_active: List[BaseTaskNode] = []

        for node in self.active:
            prev_node = self.prev.get(node)

            # 1) on exécute un pas de la tâche
            done = node.handle(ctx)

            if not done:
                # toujours en cours → on garde le nœud
                next_active.append(node)
                continue

            # 2) on collecte les transitions dont can_fire(prev, ctx) == True
            valid: List[BaseTransition] = [
                t
                for t in node.transitions
                if t.can_transit(current=prev_node, target=node, ctx=ctx)
            ]

            if not valid:
                # pas de suite → le nœud disparaît
                continue

            if self.parallel:
                # on enrichit toutes les branches
                for t in valid:
                    next_active.append(t.target)
                    self.prev[t.target] = node
            else:
                # on suit la transition menant au nœud au score maximal
                best = max(valid, key=lambda t: t.target.score(prev_node, ctx))
                next_active.append(best.target)
                self.prev[best.target] = node

        self.active = next_active
