import point
import area

class RectangleArena:
    """Represent the arena
    """
    def __init__(self, own_parterres, own_protect_parterres,rival_own_parterres, rival_own_protect_parterres, zones_plants, starting_position : point, origin : point = point(0,0), opposite_corner : point = point(2,3)):
        self.zone_plants = zones_plants
        self.own_parterres = own_parterres
        self.own_protected_parterres = own_protect_parterres
        self.rival_own_parterres = rival_own_parterres
        self.rival_own_protect_parterres = rival_own_protect_parterres
        self.origin = origin
        self.opposite_corner = opposite_corner
        self.starting_position = starting_position


    def is_in_arena(self, point : point):
        if(point.x<self.opposite_corner.x and point.y<self.opposite_corner.y and point.x>=self.origin.x and point.y>= self.origin.y):
            return True
        else:
            return False
        