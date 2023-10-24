from . import point as p
from . import area
from . import tools as t

class RectangleArena:
    """Represent the arena. Only works if it's a rectangle one
    """
    def __init__(self, starting_position : p.point = (0,0), origin : p.point = p.point(0,0), opposite_corner : p.point = p.point(200,300), plants_zone = None, own_protected_gardeners = None, own_gardeners = None, own_protected_depot_zone = None, own_depot_zone = None, rival_own_gardeners = None):
        if type(origin) == type(p.point):
            self.origin = origin
        else:
            print("origin must be a point, set to default (0,0)")
            origin = p.point(0,0)

        if type(opposite_corner) == type(p.point):
            self.opposite_corner = opposite_corner
        else :
            print("opposite_corner must be a point, set to default (200,300)")
            self.opposite_corner = p.point(2,3)

        if type(starting_position) == type(p.point):
            self.opposite_corner = opposite_corner
        else :
            print("starting position must be a point, set to default (0,0)")
            self.starting_position = p.point(0,0)

        if plants_zone == None or t.is_list_of(plants_zone,area.rectangle_area): 
            self.zone_plants = plants_zone
        else : 
            print("zones_plants must be a list of areas or none")
            self.zone_plants = None

        if own_gardeners == None or t.is_list_of(own_gardeners, area.gardener):
            self.own_gardeners = own_gardeners
        else : 
            print("zones_plants must be a list of gardener or none")
            self.own_gardeners = None

        if own_protected_gardeners == None or t.is_list_of(own_protected_gardeners,area.gardener):
            self.own_protected_gardener = own_protected_gardeners
        else :
            print("zones_plants must be a list of gardener or none")
            self.own_protected_gardener = None

        if own_protected_depot_zone == None or t.is_list_of(own_protected_depot_zone, area.depot_zone):
            self.own_protected_depot_zone = own_protected_depot_zone
        else :
            print("own_protected_depot_zone must be a list of depot zone or none")
            self.own_protected_depot_zone = None

        if own_depot_zone == None or t.is_list_of(own_depot_zone, area.depot_zone):
            self.own_depot_zone = own_depot_zone
        else :
            print("own_depot_zone must be a list of depot zone or none")
            self.own_depot_zone = None

        if rival_own_gardeners == None or t.is_list_of(rival_own_gardeners, area.gardener):
            self.rival_own_gardener = rival_own_gardeners
        else:
            print("rival_own_gardener must be a list of gardener or none")
            self.rival_own_gardener = None
        


    def is_in_arena(self, point : p.point):
        if(point.x<self.opposite_corner.x and point.y<self.opposite_corner.y and point.x>=self.origin.x and point.y>= self.origin.y):
            return True
        else:
            return False
        