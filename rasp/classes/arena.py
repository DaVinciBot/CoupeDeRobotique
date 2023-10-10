import point
import area
import tools as t

class RectangleArena:
    """Represent the arena. Only works if it's a rectangle one
    """
    def __init__(plants_zone, rival_own_gardeners, rival_own_protected_gardeners, own_gardeners, own_protected_gardener, own_depot_zone, self, origin : point = point(0,0), opposite_corner : point = point(2,3), starting_position : point = (0,0)):
        
        test = True
        # verify that zones plants is a list of areas or is none
        if t.is_list_of(plants_zone,area) or plants_zone == None: 
            self.zone_plants = plants_zone
        # verify that own_gardeners is a list of areas or is none
        else : print("zones_plants must be a list of areas")
        if t.is_list_of(own_gardeners, area):
            self.own_gardeners = own_gardeners
        else : print("zones_plants ")
        
        self.own_protected_gardener = own_protected_gardener
        self.rival_own_gardener = rival_own_gardeners
        self.rival_own_protect_fardener = rival_own_protected_gardeners
        self.origin = origin
        self.opposite_corner = opposite_corner
        self.starting_position = starting_position


    def is_in_arena(self, point : point):
        if(point.x<self.opposite_corner.x and point.y<self.opposite_corner.y and point.x>=self.origin.x and point.y>= self.origin.y):
            return True
        else:
            return False
        