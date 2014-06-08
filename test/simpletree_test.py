import unittest

from simpletree import *


class Test_SingleNode(unittest.TestCase):
    def setUp(self):
        self.node = TreeNode(data_ = {'first':'a',
                                      'second':'b',
                                      'third':'c'})

    def test_construction_data(self):
        #default no data
        node = TreeNode()
        self.assertEqual(node.data, {})
        #with data_ argument construction
        byhand_data = {'first':'a',
                       'second':'b',
                       'third':'c'}
        self.assertEqual(self.node.data, byhand_data)
        #with arbitrary keyword arguments construction
        node = TreeNode(first='a',
                        second='b',
                        third='c')
        self.assertEqual(node.data, byhand_data)

    def test_eq_ne(self):
        node1 = self.node
        node1a = node1
        node2 = TreeNode()
        self.assertEqual(node1, node1a)
        self.assertNotEqual(node1, node2)

    def test_graft(self):
        child = TreeNode()
        self.node.graft(child)
        #assert dual link
        self.assertEqual(list(self.node.children())[0], child)
        self.assertEqual(self.node, child.parent())
        #assert correct children array
        self.assertEqual(list(self.node.children()), [child])

    def test_depth(self):
        self.assertEqual(self.node.depth(), 0)

    def test_children_by_data(self):
        self.assertEqual(list(self.node.children_by_data('first','a')), [])

    def test_route_to_root(self):
        self.assertEqual(list(self.node.route_to_root()), [self.node])

    def test_route_from_root(self):
        self.assertEqual(list(self.node.route_from_root()), [self.node])

    def test_traverse(self):
        self.assertEqual(list(self.node.traverse()), [self.node])

    def test_traverse_post_order(self):
        self.assertEqual(list(self.node.traverse_post_order()), [self.node])

    def test_leaves(self):
        self.assertEqual(list(self.node.leaves()), [self.node])

    def test_trim(self):
        self.node.trim()
        self.assertEqual(self.node.parent(), None)
        self.assertEqual(list(self.node.children()), [])

    def test_trim_dead_branch(self):
        self.node.trim_dead_branch()
        self.assertEqual(self.node.parent(), None)
        self.assertEqual(list(self.node.children()), [])

    def test_degenerate_to_leaf(self):
        self.node.degenerate_to_leaf(self.node)
        self.assertEqual(self.node.parent(), None)
        self.assertEqual(list(self.node.children()), [])

    def test_getitem(self):
        #test existing data
        data_list = [self.node['first'],self.node['second'],self.node['third']]
        byhand_data_list = ['a','b','c']
        self.assertEqual(data_list, byhand_data_list)

    def test_setitem(self):
        #change one item
        self.node['second'] = 'bb'
        #make sure all other items are still the same
        data_list = [self.node['first'],self.node['second'],self.node['third']]
        byhand_data_list = ['a','bb','c']
        self.assertEqual(data_list, byhand_data_list)
        
    def test_search(self):
        #test for existing data
        data_items = {'first':'a', 'third':'c'}
        self.assertEqual(list(self.node.search(data_items)), [self.node])
        #test for non-existent data
        data_items = {'first':'aa', 'third':'cc'}
        self.assertEqual(list(self.node.search(data_items)), [])


class Test_Tree(unittest.TestCase):
    def setUp(self):
        #create a 3 level tree (root, first, second)
        self.root = TreeNode(name='root')
        #add 3 children to root
        for i in range(3):
            node = TreeNode()
            self.root.graft(node)
            node['name'] = node.parent()['name'] + ',' + str(i)
            self.L1_node = node
        #add 3 children to only the last of the previous children
        for i in range(3):
            node = TreeNode()
            self.L1_node.graft(node)
            node['name'] = node.parent()['name'] + ',' + str(i)
            self.L2_node = node
        #create various byhand data for testing
        self.byhand_L1_route = [self.L1_node, self.root]
        self.byhand_L2_route = [self.L2_node, self.L1_node, self.root]
        self.byhand_traversal_names = ['root',
                                       'root,0','root,1','root,2',
                                       'root,2,0','root,2,1','root,2,2']
        self.byhand_leaf_names = ['root,0','root,1',
                                  'root,2,0','root,2,1','root,2,2']
        
    def test_graft(self):
        #graft onto the L1 node
        child = TreeNode()
        self.L1_node.graft(child)
        child['name'] = child.parent()['name'] + ',' + 'graft'
        #assert dual link
        self.assertIn(child, self.L1_node.children())
        self.assertEqual(self.L1_node, child.parent())
        #assert correct children array
        self.assertEqual(list(child.children()), [])

    def test_depth(self):
        self.assertEqual(self.root.depth(), 0)
        self.assertEqual(self.L1_node.depth(), 1)
        self.assertEqual(self.L2_node.depth(), 2)

    def test_children_by_data(self):
        self.assertEqual(list(self.root.children_by_data('name','root,2')),
                         [self.L1_node])
        self.assertEqual(list(self.L1_node.children_by_data('name','root,2,2')),
                         [self.L2_node])
        

    def test_route_to_root(self):
        #test from L1
        self.assertEqual(list(self.L1_node.route_to_root()),
                         self.byhand_L1_route)
        #test from L2
        self.assertEqual(list(self.L2_node.route_to_root()),
                         self.byhand_L2_route)

    def test_route_from_root(self):
        #test to L1
        self.assertEqual(list(self.L1_node.route_from_root()),
                         list(reversed(self.byhand_L1_route)))
        #test to L2
        self.assertEqual(list(self.L2_node.route_from_root()),
                         list(reversed(self.byhand_L2_route)))

    def test_traverse(self):
        traversal_names = [node['name'] for node in self.root.traverse()]
        self.assertEqual(self.byhand_traversal_names, traversal_names)

    def test_traverse_post_order(self):
        traversal_names = [node['name'] for node in
                           self.root.traverse_post_order()]
        self.assertEqual(list(reversed(self.byhand_traversal_names)),
                         traversal_names)

    def test_leaves(self):
        leaf_names = [leaf['name'] for leaf in self.root.leaves()]
        self.assertEqual(leaf_names, self.byhand_leaf_names)

    def test_trim(self):
        self.L1_node.trim()
        traversal_names = [node['name'] for node in self.root.traverse()]
        byhand_traversal_names = ['root',
                                  'root,0','root,1']
        self.assertEqual(traversal_names, byhand_traversal_names)

    def test_trim_dead_branch(self):
        #add a degenerate (dead) branch to one of the multi-child nodes
        node1 = TreeNode()
        node2 = TreeNode()
        self.L1_node.graft(node1)
        node1['name'] = node1.parent()['name'] + ',graft1'
        node1.graft(node2)
        node2['name'] = node2.parent()['name'] + ',graft2'
        self.byhand_traversal_names.extend([node1['name'], node2['name']])
                                  
        #sequentially use trim_dead_branch until only the root is left
        iterations = 0
        while list(self.root.children()):
            leaves = list(self.root.leaves())
            leaf = leaves[0]
            dead_root = leaf.trim_dead_branch()
            for node in dead_root.traverse():
                self.byhand_traversal_names.remove(node['name'])
            leaves = list(self.root.leaves())
            #assert that the tree has been modified
            traversal_names = [node['name'] for node in self.root.traverse()]
            self.assertEqual(traversal_names, self.byhand_traversal_names)
            iterations += 1
        byhand_iterations = 6
        self.assertEqual(iterations, byhand_iterations)

    def test_root_degenerate_to_leaf(self):
        #test from the full tree root
        self.root.degenerate_to_leaf(self.L2_node)
        traversal_names = [node['name'] for node in self.root.traverse()]
        byhand_traversal_names = ['root','root,2','root,2,2']
        self.assertEqual(traversal_names, byhand_traversal_names)

    def test_inner_degenerate_to_leaf(self):
        #test from an inner node
        self.L1_node.degenerate_to_leaf(self.L2_node)
        traversal_names = [node['name'] for node in self.root.traverse()]
        byhand_traversal_names = ['root','root,0','root,1','root,2','root,2,2']
        self.assertEqual(traversal_names, byhand_traversal_names)
        
    def test_search_from_root(self):
        #add duplicate so multiple results will be tested
        extra_node = TreeNode(name=self.L1_node['name'])
        self.root.graft(extra_node)
        #test for existing data
        data_items = {'name':'root'}
        self.assertEqual(list(self.root.search(data_items)), [self.root])
        data_items = {'name':self.L1_node['name']}
        self.assertEqual(list(self.root.search(data_items)), [self.L1_node,
                                                              extra_node])
        #test for non-existent data
        data_items = {'name':'__abc'}
        self.assertEqual(list(self.root.search(data_items)), [])

    def test_search_from_inner(self):
        #test for existing data
        data_items = {'name':self.L2_node['name']}
        self.assertEqual(list(self.L1_node.search(data_items)), [self.L2_node])
        #test for non-existent data
        data_items = {'name':'root'}
        self.assertEqual(list(self.L1_node.search(data_items)), [])

    def test_trim_children(self):
        self.L1_node.trim_children()
        traversal_names = [node['name'] for node in self.root.traverse()]
        byhand_traversal_names = ['root',
                                  'root,0','root,1','root,2']
        self.assertEqual(traversal_names, byhand_traversal_names)
    
if __name__ == "__main__":
    try: unittest.main()
    except SystemExit: pass
