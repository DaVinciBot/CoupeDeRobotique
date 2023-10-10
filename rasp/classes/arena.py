import point
import area

class RectangleArena:
    """Represent the arena. Only works if it's a rectangle one
    """
    def __init__(self, origin : point = point(0,0), opposite_corner : point = point(2,3), starting_position : point = (0,0), own_parterres : area = None, own_protect_parterres : area = None,rival_own_parterres : area = None, rival_own_protect_parterres : area = None, zones_plants : area = None):
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
        