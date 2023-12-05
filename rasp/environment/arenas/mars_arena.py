from environment.geometric_shapes.point import Point
from environment.geometric_shapes.rectangle import Rectangle
from environment.arenas.arena import Arena

class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024
    """

    def __init__(self, color : str = "yellow"):
        origin = Point(0,0)
        opposite_corner = Point(200,300)
        if color == "blue":
            super().__init__(origin=origin,opposite_corner=opposite_corner,forbidden_area=Rectangle(Point(0,255),Point(45,300)),home= Rectangle(Point(0,0),Point(45,45)))
        elif color == "yellow":
            super().__init__(origin=origin,opposite_corner=opposite_corner,forbidden_area=Rectangle(Point(0,0),Point(45,45)),home= Rectangle(Point(0,255),Point(45,300)))
        else :
            raise Exception("the given color doesn't exist")

    def __str__(self) -> str:
        return(
            "MarsArena :\n"
            f"\tstarting_position : {self.home.center.__str__()}\n"
            f"\torigin : {self.origin.__str__()}\n"
            f"\topposite corner : {self.opposite_corner.__str__()}\n"
            f"\trival_protected_depot_zone : {self.rival_protected_depot_zone.__str__()}\n"
            "\tplants_zone :\n"
            "\town_protected_gardeners : \n"
            "\town_gardeners\n : "
            "\town_protected_depot_zone : \n"
            "\town_depot_zone : "
        )
            