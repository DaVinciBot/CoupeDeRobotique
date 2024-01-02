from environment.geometric_shapes.point import Point
from environment.geometric_shapes.rectangle import Rectangle
from environment.arenas.arena import Arena

class MarsArena(Arena):
    """Represent the arena of the CDR 2023-2024
    """
            
    def __init__(
        self,
        forbidden_area : Rectangle,
        starting_area : Rectangle,
        home : Rectangle = None, # the area to go to at the end
        origin : Point = Point(0,0),
        opposite_corner : Point = Point(200,300)
        ):
        
        if home == None:
            home = starting_area
        super().__init__(
            forbidden_area=forbidden_area,
            starting_area=starting_area,
            home=home,origin=origin,
            opposite_corner=opposite_corner
            )

    def __str__(self) -> str:
        return "mars arena"

    def Display(self) -> str:
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
        
    
            