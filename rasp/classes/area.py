import point
import rasp.classes.point

class area:

    def __init__(self, corner1 : point,corner2 : point, corner3 : point, corner4: point):
        self.corner1 = corner1
        self.corner2 = corner2
        self.corner3 = corner3
        self.corner4 = corner4

    def rectangle_get_center(self):
        """Calculate the center of an area assuming it's a rectangle

        Returns:
            _type_: point
        """
        return point((self.corner1-self.corner2)/2, (self.corner3-self.corner4)/2)

class parterre (area):
    def __init__(self, corner1: point, corner2: point, corner3: point, corner4: point, nb_pots_max : int = 6, nb_pots : int = 0, is_full : bool = False):
        super().__init__(corner1, corner2, corner3, corner4)