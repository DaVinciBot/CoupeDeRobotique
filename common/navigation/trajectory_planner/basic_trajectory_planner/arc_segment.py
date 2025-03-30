from dataclasses import dataclass
from geometry import OrientedPoint


@dataclass
class ArcSegment:
    start: OrientedPoint
    end: OrientedPoint
    duration: float
    center_x: float
    center_y: float
    r: float  # rayon de courbure (positif)
    turn: int  # +1 pour un virage à gauche, -1 pour un virage à droite
    angle_start: float  # angle (par rapport au centre) au début de l'arc
    delta_angle: float  # variation d'angle sur l'arc (avec le signe indiquant le sens)
