import unittest

from flexframe import *

class TestNewFlexGrid(unittest.TestCase):
    def setUp(self):
        self.dimensions = ['x','y','z']
        self.sizes = [2,2,2]
        self.g = FlexGrid(*self.dimensions, initial_sizes = self.sizes)
        self.byhand_empty = [[[None,None],[None,None]],[[None,None],[None,None]]]
        self.byhand_data = [[[1,2],[3,4]],[[5,6],[7,8]]]
        self.byhand_flattened = [(1,[0,0,0]),(2,[0,0,1]),(3,[0,1,0]),(4,[0,1,1]),(5,[1,0,0]),(6,[1,0,1]),(7,[1,1,0]),(8,[1,1,1])]
        self.valid_positions = [(None, [0,0,0]),(None, [0,0,1]),(None, [0,1,0]),
                            (None, [1,0,0]),(None, [1,1,1])]
        self.invalid_positions = [[0,0,2],[0,2,0],[2,0,0],[2,2,2]]

    def test_creation(self):
        self.assertEqual(self.g._dimensions, self.dimensions)
        self.assertEqual(self.g._nodes, self.byhand_empty)
        
    def test_clear_frame_and_create_grid(self):
        self.assertEqual(self.g._nodes, self.byhand_empty)

    def test_nodes(self):
        '''Test for empty nodes since only empty objects on creation.'''
        self.assertEqual(list(self.g.nodes()), [])

    def test_repr(self):
        '''Test that an empty board is just an empty string.'''
        self.assertEqual(str(self.g), '')

    def test_look_valid(self):
        '''Test for return of empty object for valid positions.'''
        for item, position in self.valid_positions:
            self.assertEqual(self.g.look(*position), item)

    def test_look_invalid(self):
        '''Test for correct exception for invalid positions.'''
        with self.assertRaises(ValueError):
            for position in self.invalid_positions:
                self.g.look(*position)

    def test_pickup_valid(self):
        '''Test for return of and leaving of empty object and for
        valid positions.'''
        for item, position in self.valid_positions:
            self.assertEqual(self.g.pickup(*position), item)
            self.assertEqual(self.g.look(*position), None)

    def test_pickup_invalid(self):
        '''Test for correct exception for invalid positions.'''
        with self.assertRaises(ValueError):
            for position in self.invalid_positions:
                self.g.pickup(*position)

    def test_place_valid(self):
        '''Test for correct change of grid after place.'''
        counter = 1
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    self.g.place(counter, i, j, k)
                    counter += 1
        self.assertEqual(self.g._nodes, self.byhand_data)

    def test_place_invalid(self):
        '''Test for correct exception for invalid positions.'''
        with self.assertRaises(ValueError):
            for position in self.invalid_positions:
                self.g.place('duck', *position)

    def test_eq(self):
        '''Confirm equality when created with same parameters.'''
        same_g = FlexGrid(*self.dimensions, initial_sizes = self.sizes)
        self.assertEqual(self.g, same_g)

    def test_eq_different_dimensions(self):
        '''Confirm that a change of dimension name only causes inequality.'''
        diff_dimensions = ['x','y','z1']
        diff_g = FlexGrid(*diff_dimensions, initial_sizes = self.sizes)
        self.assertNotEqual(self.g, diff_g)

    def test_eq_dfiferent_sizes(self):
        '''Confirm that a change of dimension size only causes inequality.'''
        diff_sizes = [2,1,2]
        diff_g = FlexGrid(*self.dimensions, initial_sizes = diff_sizes)
        self.assertNotEqual(self.g, diff_g)





class TestFlexGridWithData(unittest.TestCase):
    def setUp(self):
        self.dimensions = ['x','y','z']
        self.sizes = [2,2,2]
        self.g = FlexGrid(*self.dimensions, initial_sizes = self.sizes)
        self.byhand_empty = [[[None,None],[None,None]],[[None,None],[None,None]]]
        self.byhand_data = [[[1,2],[3,4]],[[5,6],[7,8]]]
        self.byhand_flattened = [(1,[0,0,0]),(2,[0,0,1]),(3,[0,1,0]),(4,[0,1,1]),(5,[1,0,0]),(6,[1,0,1]),(7,[1,1,0]),(8,[1,1,1])]
        self.valid_positions = [(1, [0,0,0]),(2, [0,0,1]),(3, [0,1,0]),
                            (5, [1,0,0]),(8, [1,1,1])]
        #place some data on the grid
        counter = 1
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    self.g.place(counter, i, j, k)
                    counter += 1

    def test_clear_frame(self):
        self.g.clear_frame()
        self.assertEqual(self.g._nodes, self.byhand_empty)

    def test_repr(self):
        '''Test that an empty board is just an empty string.'''
        self.assertEqual(str(self.g), '12345678')

    def test_look_valid(self):
        '''Test for return of empty object for valid positions.'''
        for item, position in self.valid_positions:
            self.assertEqual(self.g.look(*position), item)

    def test_pickup_valid(self):
        '''Test for return of and leaving of empty object and for
        valid positions.'''
        for item, position in self.valid_positions:
            self.assertEqual(self.g.pickup(*position), item)
            self.assertEqual(self.g.look(*position), None)

    def test_place_valid(self):
        '''Test for correct change of grid after place.'''
        self.g.place('a', 0,0,0)
        self.g.place('b', 0,0,1)
        self.g.place('h', 1,1,1)
        self.byhand_data = [[['a','b'],[3,4]],[[5,6],[7,'h']]]
        self.assertEqual(self.g._nodes, self.byhand_data)

    def test_eq(self):
        '''Confirm equality when created with same parameters.'''
        same_g = FlexGrid(*self.dimensions, initial_sizes = self.sizes)
        #place same data on the grid
        counter = 1
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    same_g.place(counter, i, j, k)
                    counter += 1
        self.assertEqual(self.g, same_g)

    def test_eq_different_items(self):
        '''Confirm that a change of item only causes inequality.'''
        diff_g = FlexGrid(*self.dimensions, initial_sizes = self.sizes)
        #place same data on the grid
        counter = 1
        for i in range(2):
            for j in range(2):
                for k in range(2):
                    diff_g.place(counter, i, j, k)
                    counter += 1
        #change one item
        diff_g.place('a', 0,0,0)
        self.assertNotEqual(self.g, diff_g)









class TestPositionConstruction(unittest.TestCase):
    def test_one_dimension(self):
        p1 = FlexPosition(['distance',5])
        self.assertEqual(p1._dimensions,['distance'])
        self.assertEqual(p1.distance, 5)

    def test_two_dimensions(self):
        p1 = FlexPosition(['distance',5], ['angle',90])
        self.assertEqual(p1._dimensions,['distance','angle'])
        self.assertEqual(p1.distance, 5)
        self.assertEqual(p1.angle, 90)

    def test_three_dimensions(self):
        p1 = FlexPosition(['distance',5], ['angle',90], ['day','saturday'])
        self.assertEqual(p1._dimensions,['distance','angle','day'])
        self.assertEqual(p1.distance, 5)
        self.assertEqual(p1.angle, 90)
        self.assertEqual(p1.day, 'saturday')
        
    def test_standard_separators(self):
        p1 = FlexPosition(['distance',5], ['angle',90], ['day','saturday'])
        self.assertEqual(p1._separators, [['(',''],[',',''],[',',')']])

    def test_custom_separators(self):
        p1 = FlexPosition(['distance',5], ['angle',90], ['day','saturday'],
                          separators = [['<<','-'],['_','+'],['=','>>']])
        self.assertEqual(p1._separators, [['<<','-'],['_','+'],['=','>>']])
        
class TestPosition__repr__(unittest.TestCase):
    def test_standard_separators(self):
        p1 = FlexPosition(['distance',5], ['angle',90], ['day','saturday'])
        self.assertEqual(str(p1), '(5,90,saturday)')

    def test_custom_separators(self):
        p1 = FlexPosition(['distance',5], ['angle',90], ['day','saturday'],
                          separators = [['<<','-'],['_','+'],['=','>>']])
        self.assertEqual(str(p1), '<<5-_90+=saturday>>')

class TestPosition__eq__(unittest.TestCase):
    def setUp(self):
        self.p1 = FlexPosition(['distance',5], ['angle',90])
        self.p2 = FlexPosition(['distance',5], ['angle',90], 
                               separators = [['(',''],['<',')']])
        self.p3 = FlexPosition(['angle',90], ['distance',5])
        self.p4 = FlexPosition(['distance',50], ['angle',90])

    def test_eq(self):
        self.assertEqual(self.p1,self.p2) #e.g. separators not involved
        self.assertNotEqual(self.p1,self.p3)
        self.assertNotEqual(self.p1,self.p4)
        self.assertNotEqual(self.p2,self.p3)
        self.assertNotEqual(self.p2,self.p4)
        self.assertNotEqual(self.p3,self.p4)


class TestConstruction(unittest.TestCase):
    def setUp(self):
        pass








class TestLook(unittest.TestCase):
    def setUp(self):
        pass








class TestPickup(unittest.TestCase):
    def setUp(self):
        pass








class TestPlace(unittest.TestCase):
    def setUp(self):
        pass








class TestDeletePosition(unittest.TestCase):
    def setUp(self):
        pass








class TestNodes(unittest.TestCase):
    def setUp(self):
        pass








class Test__eq__(unittest.TestCase):
    def setUp(self):
        pass








class test__sub__(unittest.TestCase):
    def setUp(self):
        pass








class test__contains__(unittest.TestCase):
    def setUp(self):
        pass








class TestClone(unittest.TestCase):
    def setUp(self):
        pass








class TestLoadContent(unittest.TestCase):
    def setUp(self):
        pass








class TestSerializePositions(unittest.TestCase):
    def setUp(self):
        pass








class Test__Repr__(unittest.TestCase):
    def setUp(self):
        pass






if __name__ == "__main__":
    try: unittest.main()
    except SystemExit: pass
