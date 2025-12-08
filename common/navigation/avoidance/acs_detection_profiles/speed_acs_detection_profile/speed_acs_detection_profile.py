"""Speed-based ACS detection profile (ally + enemy) using closest-approach / TTC."""

from __future__ import annotations

import time
from typing import TYPE_CHECKING, Tuple

from log_manager import LogLogger
import numpy as np

from navigation.avoidance.acs_detection_profiles.base_acs_detection_profiles.base_acs_detection_profiles import (  # noqa: E501
    BaseAcsDetectionProfile,
)

from navigation.avoidance.acs_detection_profiles.speed_acs_detection_profile.speed_acs_detection_profile_params import (  # noqa: E501
    SpeedAcsDetectionProfileParams,
)

if TYPE_CHECKING:
    from arena.base_arena.arena_zones import AllyZone, EnemyZone
    from loggerplusplus import Logger


class SpeedAcsDetectionProfile(BaseAcsDetectionProfile[SpeedAcsDetectionProfileParams]):
    """
    ACS detection profile based on both ally and enemy velocities using closest-approach. NASA approved method 😎.

    Args:
        params (SpeedAcsDetectionProfileParams): Parameters for the speed-based ACS detection profile.
        logger (Logger | None, optional):
            Logger instance for debugging. Defaults to None.

    """
    def __init__(self, params: SpeedAcsDetectionProfileParams, logger=None) -> None:
        self.params: SpeedAcsDetectionProfileParams = params
        self._logger: Logger = logger or LogLogger(
            identifier=self.__class__.__name__,
            follow_logger_manager_rules=True,
        )
        self.last_p1 = None
        self.last_time = None

        super().__init__(params, logger)

    def _time_and_distance_to_closest_approach(self, p1: np.ndarray, v1: np.ndarray, p2: np.ndarray, v2: np.ndarray,
                                               eps: float = 1e-4) -> Tuple[float, float]:
        # random af le 10^-4 cm/s
        # je sais pas si c cm/s ou m/s, je pense c cm/s
        """
        Compute the time t* and distance d* at which two moving points reach their closest separation.

        Args:
            p1 (np.ndarray): Position of point 1 (2D).
            v1 (np.ndarray): Velocity of point 1 (2D).
            p2 (np.ndarray): Position of point 2 (2D).
            v2 (np.ndarray): Velocity of point 2 (2D).
            eps (float, optional): Threshold to treat relative velocity as zero.

        Returns:
            Tuple[float, float]: (t_star, d_star) with t_star the time of closest approach
            and d_star the separation distance at that instant.
        """
        # genre np.dot c le produit vectoriel et np.linalg.norm la norme d'un vecteur je crois je capte pas trop
        # frr je déteste numpy
        # je veux plus faire des maths avec des matrices oskour
        # la vérité je capte rien je réécris la formule de la NASA c tout

        p: np.ndarray = p2 - p1
        v: np.ndarray = v2 - v1
        vv: np.ndarray = np.dot(v, v)

        if vv < eps:
            t_star: float = 0.0
            d_star: float = float(np.linalg.norm(p))
            return t_star, d_star

        t_star: float = float(-np.dot(p, v) / vv)
        t_star: float = max(0.0, min(t_star, self.params.horizon))

        d_vec: np.ndarray = p + v * t_star
        d_star: float = float(np.linalg.norm(d_vec))

        return t_star, d_star

    def is_acs_triggered(self, ally_zone: AllyZone, enemy_zone: EnemyZone) -> bool:
        """
        Determine whether ACS should trigger using ally and enemy speed.

        Args:
            ally_zone (AllyZone): The robot's current zone.
            enemy_zone (EnemyZone): The detected enemy zone.

        Returns:
            bool: True if ACS should trigger, False otherwise.
        """
        p1: np.ndarray = np.array([ally_zone.point.x, ally_zone.point.y])

        t_now: float = time.time()
        if self.last_p1 is None:
            v1: np.ndarray = np.array([0.0, 0.0])
        else:
            dt: float = t_now - self.last_time
            if dt <= 1e-4:  # c random la valeur mais marre d'avoir des : on divise pas par 0 gnagna maths maths maths
                v1: np.ndarray = np.array([0.0, 0.0])
            else:
                v1: np.ndarray = (p1 - self.last_p1) / dt

        self.last_p1 = p1
        self.last_time = t_now

        p2: np.ndarray = np.array([enemy_zone.point.x, enemy_zone.point.y])
        enemy_vec = enemy_zone.speed_vector
        v2: np.ndarray = np.array([enemy_vec.factored_dx, enemy_vec.factored_dy])

        t_star, d_star = self._time_and_distance_to_closest_approach(p1, v1, p2, v2)

        v1_speed: float = float(np.linalg.norm(v1))
        v2_speed: float = float(np.linalg.norm(v2))

        d_safe: float = self.params.acs_distance + self.params.reaction_time * (v1_speed + v2_speed)

        self._logger.debug(
            f"[SpeedACS] t*={t_star: .2f} s, d*={d_star: .2f} cm, v1={v1_speed: .2f} cm/s, "
            f"v2={v2_speed: .2f} cm/s, d_safe={d_safe: .2f} cm"
        )

        if d_star <= d_safe:
            self._logger.debug(f"[NAV:ACS] Triggered: - distance: {d_star: .1f} cm")
            return True

        if t_star <= self.params.min_tcc:
            self._logger.debug(f"[NAV:ACS] Triggered: - time to closest approach: {t_star: .2f} s")
            return True

        return False
