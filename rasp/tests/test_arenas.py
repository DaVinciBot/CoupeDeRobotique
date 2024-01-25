import pytest
from bot import MarsArena, Arenas
from bot.Shapes import Point, Rectangle


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
        for i in range(len(arena.plant_areas)):
            if i%2 != 0 and arena.is_our_zone(arena.plant_areas[i],arena.plant_areas):
                verif = False
                break
            if i%2 == 0 and not arena.is_our_zone(arena.plant_areas[i][0],arena.plant_areas):
                verif = False
                break
        assert verif