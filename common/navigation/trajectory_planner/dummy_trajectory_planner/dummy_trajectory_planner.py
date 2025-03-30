import math
from math import sqrt, sin, cos, atan2
from dataclasses import dataclass
from loggerplusplus import Logger
from geometry import OrientedPoint
from navigation.trajectory_planner.structs import TrajectoryPlanCommand
from navigation.trajectory_planner.base_trajectory_planner.base_trajectory_planner import BaseTrajectoryPlanner
from navigation.trajectory_planner.dummy_trajectory_planner.dummy_trajectory_planner_params import \
    DummyTrajectoryPlannerParams

from navigation.trajectory_planner.speed_profile import SpeedProfiler


# Définition des segments internes pour la planification séquentielle
@dataclass
class TurnSegment:
    start: OrientedPoint  # pose de départ pour la rotation
    target_angle: float  # angle final visé pour s'orienter vers le but
    angular_distance: float  # valeur absolue de la rotation à effectuer (en radians)
    duration: float  # durée du segment (calculée via le speed_profile)
    direction: int  # +1 si rotation trigonométrique, -1 sinon


@dataclass
class StraightSegment:
    start: OrientedPoint  # pose de départ (après rotation)
    end: OrientedPoint  # pose cible
    distance: float  # distance à parcourir
    duration: float  # durée du segment (calculée via le speed_profile)


@dataclass
class StopSegment:
    position: OrientedPoint  # position où s'arrêter
    duration: float  # durée de l'arrêt (step_sleep_delay)


class DummyTrajectoryPlanner(BaseTrajectoryPlanner[DummyTrajectoryPlannerParams]):
    def __init__(self, params: DummyTrajectoryPlannerParams, speed_profiler: SpeedProfiler,
                 logger: Logger | None = None) -> None:
        # On passe les paramètres, le speed_profiler et éventuellement un logger à la classe de base.
        super().__init__(params, speed_profiler, logger)
        self.segments: list[object] = []  # Contiendra TurnSegment, StraightSegment ou StopSegment
        self.total_duration: float = 0.0

    def _compute_total_time(self, distance: float, max_speed: float, acceleration: float) -> float:
        """
        Calcule la durée totale pour une trajectoire de 'distance' donnée,
        en partant et finissant à 0 vitesse, selon un profil (triangulaire ou trapézoïdal).
        """
        d_acc = 0.5 * (max_speed ** 2) / acceleration
        if distance < 2 * d_acc:
            return 2 * math.sqrt(distance / acceleration)
        else:
            return (max_speed / acceleration) + ((distance - 2 * d_acc) / max_speed) + (max_speed / acceleration)

    def plan_trajectory(self, start: OrientedPoint, goal: OrientedPoint) -> TrajectoryPlanCommand:
        """
        Planifie la trajectoire de A vers B en trois phases :
          1. Rotation sur place pour s'orienter vers le but.
          2. Translation en ligne droite jusqu'au but.
          3. Arrêt sur place d'une durée définie.

        Chaque segment est traité comme une trajectoire indépendante (de 0 à 0 vitesse)
        dont la durée est calculée via le speed profiler correspondant.
        """
        self.segments = []
        self.total_duration = 0.0

        # --- Phase 1 : Rotation ---
        desired_angle = atan2(goal.y - start.y, goal.x - start.x)
        delta_angle = math.atan2(math.sin(desired_angle - start.theta), math.cos(desired_angle - start.theta))
        turn_needed = abs(delta_angle) > 1e-3
        current_pose = start

        if turn_needed:
            angular_distance = abs(delta_angle)
            # Utilisation du profil angulaire
            max_angular_speed = self.speed_profiler.angular_speed_profile.max_speed
            angular_acc = getattr(self.speed_profiler.angular_speed_profile, "acceleration", 1.0)
            turn_duration = self._compute_total_time(angular_distance, max_angular_speed, angular_acc)
            turn_segment = TurnSegment(
                start=current_pose,
                target_angle=desired_angle,
                angular_distance=angular_distance,
                duration=turn_duration,
                direction=1 if delta_angle >= 0 else -1
            )
            self.segments.append(turn_segment)
            self.total_duration += turn_duration
            # Après rotation, la nouvelle orientation est celle désirée.
            current_pose = OrientedPoint(current_pose.x, current_pose.y, desired_angle)

        # --- Phase 2 : Translation ---
        dx = goal.x - current_pose.x
        dy = goal.y - current_pose.y
        distance = sqrt(dx * dx + dy * dy)
        if distance > 1e-3:
            # Utilisation du profil linéaire
            max_linear_speed = self.speed_profiler.linear_speed_profile.max_speed
            linear_acc = getattr(self.speed_profiler.linear_speed_profile, "acceleration", 1.0)
            straight_duration = self._compute_total_time(distance, max_linear_speed, linear_acc)
            straight_segment = StraightSegment(
                start=current_pose,
                end=goal,
                distance=distance,
                duration=straight_duration
            )
            self.segments.append(straight_segment)
            self.total_duration += straight_duration
            current_pose = goal

        # --- Phase 3 : Arrêt ---
        if self.params.step_sleep_delay > 0:
            stop_segment = StopSegment(
                position=current_pose,
                duration=self.params.step_sleep_delay
            )
            self.segments.append(stop_segment)
            self.total_duration += self.params.step_sleep_delay

        # Réinitialisation du chronomètre de planification.
        self._start_trajectory_elapsed_time_checkpoint = 0.0
        self.start_planning()

        # Retourne la commande pour l'instant initial (t=0)
        return self.get_plan()

    def get_plan(self) -> TrajectoryPlanCommand:
        """
        Renvoie la commande de trajectoire (pose, vitesse linéaire et angulaire) en fonction du temps écoulé.
        Pour chaque segment, on calcule la progression (fraction du segment parcouru) et on interroge
        le profil de vitesse correspondant pour obtenir la vitesse instantanée.
        """
        elapsed = self._get_trajectory_time_elapsed()

        if elapsed >= self.total_duration:
            last_seg = self.segments[-1]
            if isinstance(last_seg, StopSegment):
                final_pose = last_seg.position
            elif isinstance(last_seg, StraightSegment):
                final_pose = last_seg.end
            elif isinstance(last_seg, TurnSegment):
                final_pose = OrientedPoint(last_seg.start.x, last_seg.start.y, last_seg.target_angle)
            else:
                final_pose = OrientedPoint(0.0, 0.0, 0.0)
            return TrajectoryPlanCommand(position=final_pose, linear_speed=0.0, angular_speed=0.0)

        time_acc = 0.0
        for seg in self.segments:
            if elapsed < time_acc + seg.duration:
                t_in_seg = elapsed - time_acc
                if isinstance(seg, TurnSegment):
                    fraction = t_in_seg / seg.duration if seg.duration > 0 else 1.0
                    current_angle = seg.start.theta + fraction * seg.direction * seg.angular_distance
                    # Appel au profil angulaire pour obtenir la vitesse actuelle
                    current_ang_speed = self.speed_profiler.angular_speed_profile.get_speed(t_in_seg,
                                                                                            seg.angular_distance) * seg.direction
                    current_pose = OrientedPoint(seg.start.x, seg.start.y, current_angle)
                    return TrajectoryPlanCommand(position=current_pose, linear_speed=0.0,
                                                 angular_speed=current_ang_speed)
                elif isinstance(seg, StraightSegment):
                    fraction = t_in_seg / seg.duration if seg.duration > 0 else 1.0
                    new_x = seg.start.x + fraction * (seg.end.x - seg.start.x)
                    new_y = seg.start.y + fraction * (seg.end.y - seg.start.y)
                    current_pose = OrientedPoint(new_x, new_y, seg.start.theta)
                    # Appel au profil linéaire pour obtenir la vitesse actuelle
                    current_lin_speed = self.speed_profiler.linear_speed_profile.get_speed(t_in_seg, seg.distance)
                    return TrajectoryPlanCommand(position=current_pose, linear_speed=current_lin_speed,
                                                 angular_speed=0.0)
                elif isinstance(seg, StopSegment):
                    return TrajectoryPlanCommand(position=seg.position, linear_speed=0.0, angular_speed=0.0)
            time_acc += seg.duration

        # Fallback : renvoie l'état final en cas d'anomalie
        last_seg = self.segments[-1]
        if isinstance(last_seg, StopSegment):
            final_pose = last_seg.position
        elif isinstance(last_seg, StraightSegment):
            final_pose = last_seg.end
        elif isinstance(last_seg, TurnSegment):
            final_pose = OrientedPoint(last_seg.start.x, last_seg.start.y, last_seg.target_angle)
        else:
            final_pose = OrientedPoint(0.0, 0.0, 0.0)
        return TrajectoryPlanCommand(position=final_pose, linear_speed=0.0, angular_speed=0.0)