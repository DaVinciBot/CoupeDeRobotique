import point
import rasp.classes.point

class rectangle_area:

    def __init__(self, corner1 : point,corner2 : point, corner3 : point, corner4: point):
        self.corner1 = corner1
        self.corner2 = corner2
        self.corner3 = corner3
        self.corner4 = corner4

    def get_center(self):
        """Calculate the center of an area assuming it's a rectangle

        Returns:
            _type_: point
        """
        return point((self.corner1-self.corner2)/2, (self.corner3-self.corner4)/2)

class pots_area (rectangle_area):
    """represents an area that contain pots

    Args:
        rectangle_area (super class)
    """
    def __init__(self, corner1: point, corner2: point, corner3: point, corner4: point,nb_pots = 6, nb_pots_max : int = 6, is_full : bool = True, is_empty : bool = False):
        self.nb_pots_max = nb_pots_max
        self.nb_pots = nb_pots
        self.is_full = is_full
        self.is_empty = is_empty
        super().__init__(corner1, corner2, corner3, corner4)
    
    def took_pot(self, n : int = 1):
        """Enable to reduce the number of pots disponible in the pots_area

        Args:
            n (int, optional): _description_. Defaults to 1.
        """
        self.nb_pots -= n
        if(self.nb_pots<=0): self.is_empty = True

    def add_pot(self, n : int = 1):
        if(self.nb_pots+n>self.nb_pots_max) : print(f"The area can't contain more than {self.nb_pots_max} pots")
        else : self.nb_pots += n
        if self.nb_pots>0 and self.is_empty == True: self.is_empty = False

    def is_empty(self):
        """Returns whereas the plant_zone is empty

        Returns:
            _type_: _description_
        """
        return self.is_empty
    
    def is_full(self):
        return self.is_full
    
class gardener (pots_area):

    """The zones outside the arena that can store both soft and resistant plants 
    """

    def __init__(self, corner1 : point,corner2 : point, corner3 : point, corner4: point, nb_pots = 0, nb_pots_max: int = 6, is_full: bool = True, is_empty: bool = False):
        super().__init__(corner1, corner2, corner3, corner4, nb_pots, nb_pots_max, is_full, is_empty)

    def physically_add_pot(self, n: int = 1):
        print("this function will allow the robot to add a pot in the gardener")

class depot_zone(pots_area):

    """the zone in the area that can store resistant plants
    """

    def __init__(self, corner1 : point,corner2 : point, corner3 : point, corner4: point, nb_pots = 0, nb_pots_max: int = 6, is_full: bool = True, is_empty: bool = False):
        super().__init__(corner1, corner2, corner3, corner4, nb_pots, nb_pots_max, is_full, is_empty)

    def physically_add_pot(self, n: int = 1):
        print("this function will allow the robot to add a pot in the depot_zone")
