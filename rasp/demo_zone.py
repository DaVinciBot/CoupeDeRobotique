from bot.Shapes import Rectangle, OrientedPoint, Point
from bot.tools import *
import time
from bot import MarsArena, RollingBasis, State, Lidar, Actuators
from bot.tools import compute_go_to_destination
from bot.Utils import Utils
from bot.Logger import Logger

def go_to(__object : object,  distance = 0, nb_digits : int = 2, closer = True)->bool:
    destination_point = compute_go_to_destination(rolling_basis.odometrie,__object,distance,nb_digits=nb_digits,closer=closer)
    if isinstance(destination_point,OrientedPoint):
        if State.go_to_verif:
            if arena.enable_go_to(rolling_basis.odometrie,destination_point):
                rolling_basis.Go_To(destination_point)
                return True
            return False
        rolling_basis.Go_To(destination_point)
        return True
    return False

lidar = Lidar()
arena = MarsArena(0)
l = Logger()
rolling_basis = RollingBasis()

rolling_basis.Reset_Odo()
go_to(arena.drop_zones[0])