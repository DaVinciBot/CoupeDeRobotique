# ====== Standard Library Imports ======
from abc import ABC, abstractmethod
from typing import Generic, TypeVar
import time
import math

# ====== Third-Party Imports ======
from loggerplusplus import Logger

# ====== Internal Project Imports ======
from geometry import OrientedPoint

# ====== Local Imports ======
from navigation.trajectory_planner.structs import TrajectoryPlanCommand
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner
from navigation.trajectory_planner.basic_trajectory_planner.basic_trajectory_planner_params import \
    BasicTrajectoryPlannerParams
from navigation.trajectory_planner.basic_trajectory_planner.linear_segment import LineSegment
from navigation.trajectory_planner.basic_trajectory_planner.arc_segment import ArcSegment


# TODO: aucune gestion des angles de fin debut !

class BasicTrajectoryPlanner(BaseTrajectoryPlanner[BasicTrajectoryPlannerParams]):
    def __init__(self, params: BasicTrajectoryPlannerParams, logger: Logger | None = None):
        super().__init__(params, logger)
        # On stocke une liste de segments, qui seront soit des segments linéaires, soit des arcs.
        self.segments: list[object] = []  # LineSegment ou ArcSegment
        self.total_duration: float = 0.0

    def plan_trajectory(self, path: list[OrientedPoint], **kwargs) -> None:
        """
        Pour chaque paire de points consécutifs du chemin, on calcule un segment de trajectoire.
        Si l'orientation actuelle est déjà alignée avec la direction du but, on effectue un
        déplacement en ligne droite. Sinon, on calcule un arc circulaire qui part de la position
        de départ avec l'orientation initiale du robot et qui mène au point cible.
        """
        self.segments = []
        self.total_duration = 0.0
        eps = 1e-3  # seuil pour considérer une différence d'angle comme négligeable

        for i in range(len(path) - 1):
            start = path[i]
            end = path[i + 1]
            dx = end.x - start.x
            dy = end.y - start.y
            distance = math.sqrt(dx * dx + dy * dy)

            # La direction souhaitée (vers le point cible)
            phi = math.atan2(dy, dx)
            # Différence entre l'orientation actuelle et la direction vers le but.
            delta_heading = math.atan2(math.sin(phi - start.theta), math.cos(phi - start.theta))

            if abs(delta_heading) < eps:
                # On considère ce segment comme une translation en ligne droite.
                duration = distance / self.params.max_linear_speed if self.params.max_linear_speed > 0 else 0.0
                segment = LineSegment(start=start, end=end, duration=duration, direction=phi)
            else:
                # Sinon, on planifie un arc circulaire.
                # On utilise une méthode géométrique qui consiste à calculer le centre du cercle
                # qui permet de partir de start (avec orientation start.theta) et d'atteindre end.
                # La formule utilisée est : R = - (distance²) / (2*(dx*sin(start.theta) - dy*cos(start.theta)))
                denom = 2 * (dx * math.sin(start.theta) - dy * math.cos(start.theta))
                # Si le dénominateur est trop faible, on considère une translation.
                if abs(denom) < eps:
                    duration = distance / self.params.max_linear_speed if self.params.max_linear_speed > 0 else 0.0
                    segment = LineSegment(start=start, end=end, duration=duration, direction=phi)
                else:
                    R = - (distance * distance) / denom
                    r = abs(R)
                    # Le signe de R indique le sens du virage.
                    turn = 1 if R > 0 else -1

                    # Calcul du centre du cercle.
                    # Pour un virage à gauche (turn = 1), le centre se trouve à :
                    # (x0 - r*sin(start.theta), y0 + r*cos(start.theta))
                    center_x = start.x - turn * r * math.sin(start.theta)
                    center_y = start.y + turn * r * math.cos(start.theta)

                    # Calcul des angles (par rapport au centre) pour start et end.
                    angle_start = math.atan2(start.y - center_y, start.x - center_x)
                    angle_goal = math.atan2(end.y - center_y, end.x - center_x)
                    raw_delta = angle_goal - angle_start
                    # Ramener raw_delta dans [-pi, pi]
                    raw_delta = math.atan2(math.sin(raw_delta), math.cos(raw_delta))
                    # Ajuster pour que le virage suive le bon sens.
                    if turn == 1 and raw_delta < 0:
                        raw_delta += 2 * math.pi
                    elif turn == -1 and raw_delta > 0:
                        raw_delta -= 2 * math.pi

                    delta_angle = raw_delta
                    arc_length = r * abs(delta_angle)
                    duration = arc_length / self.params.max_linear_speed if self.params.max_linear_speed > 0 else 0.0

                    segment = ArcSegment(
                        start=start,
                        end=end,
                        duration=duration,
                        center_x=center_x,
                        center_y=center_y,
                        r=r,
                        turn=turn,
                        angle_start=angle_start,
                        delta_angle=delta_angle
                    )
            self.segments.append(segment)
            self.total_duration += segment.duration

        # Réinitialisation du chronomètre de planification.
        self._start_trajectory_elapsed_time_checkpoint = 0.0
        self.start_planning()

    def get_plan(self, **kwargs) -> TrajectoryPlanCommand:
        """
        En fonction du temps écoulé depuis le début de la planification, renvoie
        une commande qui inclut la position (x, y, theta) du robot et ses vitesses linéaire et angulaire.
        Pour un segment en ligne, la position est interpolée linéairement.
        Pour un arc, la position est calculée le long de la courbe circulaire, et l'orientation est
        donnée par la tangente de la courbe (orientation = angle sur le cercle + (pi/2)*turn).
        """
        if not self.segments:
            default_point = OrientedPoint(0.0, 0.0, 0.0)
            return TrajectoryPlanCommand(position=default_point, linear_speed=0.0, angular_speed=0.0)

        if not self.is_planning_started():
            self.start_planning()

        elapsed = self._get_trajectory_time_elapsed()

        # Si le temps écoulé dépasse la durée totale, renvoyer la commande finale avec vitesses nulles.
        if elapsed >= self.total_duration:
            last_seg = self.segments[-1]
            if isinstance(last_seg, LineSegment):
                final_pose = last_seg.end
            elif isinstance(last_seg, ArcSegment):
                final_pose = last_seg.end
            else:
                final_pose = OrientedPoint(0.0, 0.0, 0.0)
            return TrajectoryPlanCommand(position=final_pose, linear_speed=0.0, angular_speed=0.0)

        # Identifier dans quel segment se situe l'instant t
        time_acc = 0.0
        for seg in self.segments:
            if elapsed < time_acc + seg.duration:
                t_in_seg = elapsed - time_acc
                fraction = t_in_seg / seg.duration if seg.duration > 0 else 1.0

                if isinstance(seg, LineSegment):
                    # Interpolation linéaire pour le déplacement
                    new_x = seg.start.x + fraction * (seg.end.x - seg.start.x)
                    new_y = seg.start.y + fraction * (seg.end.y - seg.start.y)
                    new_theta = seg.direction
                    lin_speed = self.params.max_linear_speed
                    ang_speed = 0.0
                elif isinstance(seg, ArcSegment):
                    # Calcul de l'angle courant sur le cercle
                    current_angle = seg.angle_start + fraction * seg.delta_angle
                    # Position sur l'arc
                    new_x = seg.center_x + seg.r * math.cos(current_angle)
                    new_y = seg.center_y + seg.r * math.sin(current_angle)
                    # L'orientation est la tangente à l'arc.
                    new_theta = current_angle + (math.pi / 2) * seg.turn
                    lin_speed = self.params.max_linear_speed
                    # Vitesse angulaire constante (v/r) avec le signe du virage.
                    ang_speed = (self.params.max_linear_speed / seg.r) * seg.turn
                current_position = OrientedPoint(new_x, new_y, new_theta)
                return TrajectoryPlanCommand(position=current_position, linear_speed=lin_speed, angular_speed=ang_speed)
            time_acc += seg.duration

        # Par sécurité, retourner l'état final.
        last_seg = self.segments[-1]
        if isinstance(last_seg, LineSegment):
            final_pose = last_seg.end
        else:
            final_pose = last_seg.end
        return TrajectoryPlanCommand(position=final_pose, linear_speed=0.0, angular_speed=0.0)
