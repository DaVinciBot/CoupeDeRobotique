# py -m unittest discover

import unittest
import sys
import os

# necessary for direct launch
"""current_directory = os.path.dirname(os.path.abspath(__file__))
geometric_shapes = os.path.join(current_directory, "../geometric_shapes")
sys.path.append(geometric_shapes)"""

# works with the py -m unittest discover commands launched from Perso_cdr 
from geometric_shapes.point import Point
from geometric_shapes.tools import *
from geometric_shapes.rectangle import Rectangle
from arenas.mars_arena import MarsArena

class Testpoint(unittest.TestCase):
    
    def test_add(self):
        p2 = Point(12,3)
        p1 = Point(-2,2.5)
        p3 = Point(10,5.5)
        if p1+p2 != p3: self.fail()
    
    def test_sub(self):
        p1 = Point(12,3)
        p2 = Point(-2,2.5)
        p3 = Point(14,0.5)
        if p1-p2 != p3: self.fail()
    
    def test_str(self):
        p1 = Point(12,3)
        self.assertEqual(p1.__str__(), "Point(x=12, y=3)")

class Testrectangle(unittest.TestCase):
    def test_constructor(self):
        p2 = Point(12,3)
        p1 = Point(-2,2.5)
        r1 = Rectangle(p1,p2)
        if r1.corner.x != -2 or r1.corner.y != 2.5 or r1.opposite_corner.x != 12 or r1.opposite_corner.y != 3 : self.fail()

    def test_is_in_inside(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_inside = Point(2.0, 2.0)
        self.assertTrue(r.is_in(point_inside))

    def test_is_in_outside(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_outside = Point(5.0, 5.0)
        self.assertFalse(r.is_in(point_outside))

    def test_is_in_on_boundary(self):
        corner = Point(0.0, 0.0)
        opposite_corner = Point(4.0, 4.0)
        r = Rectangle(corner, opposite_corner)
        point_on_boundary = Point(4.0, 4.0)
        self.assertTrue(r.is_in(point_on_boundary))

class Testtools(unittest.TestCase):
    def test_is_lis_of(self):
        a=Point(5,6)
        b=Point(8,8.3)
        c=Point(7.8,3)
        d = None
        l1 = [a,b,c]
        l2 = l1+[d]
        l3 = [Rectangle(a,b), Rectangle(c,b)]
        self.assertTrue(is_list_of(l1,Point))
        self.assertFalse(is_list_of(l2,Point))
        self.assertTrue(is_list_of(l3,Rectangle))