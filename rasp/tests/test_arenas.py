import pytest
from bot import MarsArena, Arenas
from bot.Shapes import Point, Rectangle, Circle


class TestArena():
    def test_enable_go_to(self):
        arena = Arenas.Arena(forbidden_area=Rectangle(Point(7, 4), Point(4, 7)))
        a = Point(1, 1)
        b = Point(4, 11)
        c = Point(9,6)
        # check without width
        assert arena.enable_go_to(a, b, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(b, c, robot_width=0, robot_length=0)
        assert not arena.enable_go_to(c, a, robot_width=0, robot_length=0)
        assert arena.enable_go_to(b, a, robot_width=0, robot_length=0.01)
        assert arena.enable_go_to(c, b, robot_width=0, robot_length=0)
        assert not arena.enable_go_to(a, c, robot_width=0, robot_length=0)
        
        # check case y=constant
        d = Point(6, 1)
        e = Point(6,8)
        f = Point(9,1)
        g = Point(9,8)
        assert not arena.enable_go_to(d,e)
        assert arena.enable_go_to(f,g)
        
        # check case x=constant
        h = Point(3, 5)
        i = Point(11,4)
        j = Point(1,9)
        k = Point(11,9)
        assert not arena.enable_go_to(h,i)
        assert arena.enable_go_to(j,k)
        
        # check with width
        assert not arena.enable_go_to(b, c, robot_width=3, robot_length=0)
        assert not arena.enable_go_to(f,g,robot_width=2)
        assert not arena.enable_go_to(j,k,robot_width=3)
        
        # check border_collision
        assert arena.enable_go_to(f,a)
        assert not arena.enable_go_to(f,a,robot_length=10)
        l = Point(195,150)
        assert arena.enable_go_to(i,l)
        assert not arena.enable_go_to(i,l,robot_length=10.1)
        
        


class TestMarsArena:
    def test_enable_go_to(self):
        arena = MarsArena(1)
        assert arena.enable_go_to(Point(10, 10), Point(100, 100))
        assert arena.enable_go_to(Point(10, 10), Point(100, 100))
        assert not arena.enable_go_to(Point(10, 10), Point(100, 400))
        assert not arena.enable_go_to(Point(10, 10), Point(10, 275))
    
    def test_is_our_zone(self):
        arena = MarsArena(0)
        verif = True
        for i in range(len(arena.drop_zones)):
            if i%2 != 0 and arena.is_our_zone(arena.drop_zones[i],arena.drop_zones):
                verif = False
                break
            if i%2 == 0 and not arena.is_our_zone(arena.drop_zones[i][0],arena.drop_zones):
                verif = False
                break
        assert verif
        for i in range(len(arena.gardeners)):
            if i%2 != 0 and arena.is_our_zone(arena.gardeners[i],arena.gardeners):
                verif = False
                break
            if i%2 == 0 and not arena.is_our_zone(arena.gardeners[i][0],arena.gardeners):
                verif = False
                break
        assert verif
        for i in range(len(arena.plant_zones)):
            if i%2 != 0 and arena.is_our_zone(arena.plant_zones[i],arena.plant_zones):
                verif = False
                break
            if i%2 == 0 and not arena.is_our_zone(arena.plant_zones[i][0],arena.plant_zones):
                verif = False
                break
        assert verif
        
    def test_closest_zone(self):
        arena = MarsArena(0)
        gardeners = [
            (Rectangle(Point(77.5,-15), Point(45,-3)),False),  # 0 - Blue
            (Rectangle(Point(155,-15), Point(122.5,-3)),False),  # 1 - Yellow
            (Rectangle(Point(77.5,303), Point(45,315)),False),  # 2 - Blue
            (Rectangle(Point(155,303), Point(122.5,315)),False),  # 3 - Yellow
        ]

        # (zone,still_plants)
        plant_zones = [
            (Circle(Point(70,100),250),True),
            (Circle(Point(130,100),250),True),
            (Circle(Point(150,150),250),True),
            (Circle(Point(130,200),250),True),
            (Circle(Point(70,200),250),True),
            (Circle(Point(50,150),250),True)
        ]
        
        # (zone,is_full)
        drop_zones = [
            (Rectangle(Point(45, 0), Point(0, 45)),False),  # 0 - Blue (Possible forbidden area)
            (Rectangle(Point(122.5, 0), Point(77.5, 45)),False),  # 1 - Yellow
            (Rectangle(Point(200, 0), Point(155, 45)),False),  # 2 - Blue
            (Rectangle(Point(45, 255), Point(0, 300)),False),  # 3 - Yellow (Possible forbidden area)
            (Rectangle(Point(122.5, 255), Point(77.5, 300)),False),  # 4 - Blue
            (Rectangle(Point(200, 255), Point(155, 300)),False)  # 5 - Yellow
        ]
        p1 = Point(2,2)
        x1 = arena.closest_drop_zone(p1,exclude_not_basic=False)
        x2 = arena.closest_drop_zone(p1,our=False)
        x3 = arena.closest_gardener(p1,exclude_not_basic=False)
        x4 = arena.closest_gardener(p1,our=False)
        x5 = arena.closest_plant_zones(p1,exclude_not_basic=False)
        x6 = arena.closest_plant_zones(p1,our=False)
        r1 = [drop_zones[0],drop_zones[2],drop_zones[4]]
        r2 = [drop_zones[0],drop_zones[1],drop_zones[2],drop_zones[3],drop_zones[4],drop_zones[5]]
        r3 = [gardeners[0],gardeners[2]]
        r4 = [gardeners[0],gardeners[1],gardeners[2],gardeners[3]]
        r5 = [plant_zones[0],plant_zones[2],plant_zones[4]]
        r6 = [plant_zones[0],plant_zones[5],plant_zones[1],plant_zones[2],plant_zones[4],plant_zones[3]]
        arena = MarsArena(1)
        x7 = arena.closest_drop_zone(p1,exclude_not_basic=False)
        r7 = [drop_zones[1],drop_zones[3],drop_zones[5]]
        results = [x1,x2,x3,x4,x5,x6,x7]
        responses = [r1,r2,r3,r4,r5,r6,r7]
        for j in range(len(results)):
            for i in range(len(results[j])):
                assert results[j][i][0]==responses[j][i][0]