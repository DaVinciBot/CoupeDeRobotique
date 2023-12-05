import unittest
from geometric_shapes.point import Point
from geometric_shapes.tools import *
from geometric_shapes.rectangle import Rectangle
from arenas.arena import Arena
from arenas.mars_arena import MarsArena

class Test_arena(unittest.TestCase):

    def test_enable_go_to(self):

        arena = Arena(forbidden_area=Rectangle(Point(2,2),Point(5,5)))
        a = Point(1,1)
        b = Point(1,6)
        c = Point(3,1)
        d = Point(6,1)
        e = Point(2,6)
        f = Point(3,6)
        # check without width
        self.assertEqual(True,arena.enable_go_to(a,b,robot_width= 0,robot_length = 0.01))
        self.assertEqual(False,arena.enable_go_to(a,b,robot_width= 0, robot_length = 12.01))
        self.assertEqual(True,arena.enable_go_to(a,e,robot_width= 0, robot_length = 0.01))
        self.assertEqual(True,arena.enable_go_to(a,d,robot_width= 0, robot_length = 0.01))
        self.assertEqual(False,arena.enable_go_to(c,f,robot_width= 0, robot_length = 0.01))
        self.assertEqual(False,arena.enable_go_to(c,b,robot_width= 0,robot_length = 0.01))

        arena = Arena(forbidden_area=Rectangle(Point(5,4),Point(9,7)))
        # check with width
        a = Point(1,1)
        b= Point(4,7)
        c = Point(8,10)
        d = Point(10,7)
        e = Point(10,1)
        f = Point(2,3)
        g = Point(9,3)
        self.assertEqual(True,arena.enable_go_to(a,b,robot_width= 0,robot_length = 0.01))
        self.assertEqual(True,arena.enable_go_to(f,g,robot_width= 0, robot_length = 0.01))
        self.assertEqual(True,arena.enable_go_to(c,d,robot_width= 0, robot_length = 0.01))
        self.assertEqual(True,arena.enable_go_to(d,e,robot_width= 0,robot_length = 0.01))
        self.assertEqual(False,arena.enable_go_to(d,e,robot_width= 1,robot_length = 0.01))

class Test_mars_arena(unittest.TestCase):

    def test_enable_go_to(self):
        arena = MarsArena("blue")
        self.assertEqual(True,arena.enable_go_to(Point(10,10),Point(100,100)))
        self.assertEqual(True,arena.enable_go_to(Point(10,10),Point(100,100)))
        self.assertEqual(False,arena.enable_go_to(Point(10,10),Point(100,400)))
        self.assertEqual(False,arena.enable_go_to(Point(10,10),Point(10,275)))
