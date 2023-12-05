from point import p.Point
class Circle:
    def __init__(self, center : p.Point, radius : float):
        if(type(center)==p.Point):
            self.center = center
            self.radius = radius
        else:
            self.center = None
    
    def __str__(self) -> str:
        if self.center == None: return "Circle None"
        else: return f"Circe :\n\tcenter : {self.center}\n\tradius : {self.radius}"