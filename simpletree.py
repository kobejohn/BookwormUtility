from collections import deque

### parent and children should be made private so don't mess up linking
### parent() and children() will return their data
### but to change parent, graft/trim should be used. same for children
### check all cases of parent/children to make sure can be replaced.

class TreeNode():
    """Nodes of a tree. Each node can act as the root of it's own tree

    Public Interface:
    Focused on Node:
    data -- dictionary with arbitrary contents. accessible by [] notation
    parent()
    children()
    children_by_data()
    trim_children()
    depth()

    Focused on Tree:
    traverse()
    traverse_post_order()
    graft()
    route_to_root()
    route_from_root()
    leaves()
    trim()
    trim_dead_branch()
    degenerate_to_leaf()
    search()
    
    """

    ### get rid of either kwargs or data_. probably kwargs since less flexible
    def __init__(self, *args, data_ = None, **kwargs):
        """Construct a SimpleNode with optional data.

        keyword-only arguments:
        data_ -- a dictionary with arbitrary data

        kwargs:
        any set of name=value pairs will be (over)written in the node's data.

        """
        self._parent = None
        self._children = []
        self.data = data_ if data_ else {}
        for name, value in kwargs.items():
            self.data[name] = value
        
    def __eq__(self, other):
        if id(self) == id(other): return True
        return False

    def __ne__(self, other):
        return not self.__eq__(other)

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, value):
        self.data[key] = value

    def parent(self):
        """Return the parent of this node."""
        return self._parent

    def children(self):
        """Generate each child of this node."""
        for child in self._children:
            yield child

    def children_by_data(self, data_name, data_value):
        """Generate all children that have same data or None if not found."""
        for child in self.children():
            try:
                if child.data[data_name] == data_value: yield child
            except KeyError: continue

    def graft(self, child):
        """Append child to self's children and set child's parent to self.
        Note: For performance reasons, this assumes that child does not already
        exist in any tree connected to self rather than testing for it."""
        self._children.append(child)
        child._parent = self

    def trim(self):
        """Remove branch_root from any tree it was connected to."""
        try:
            self._parent._children.remove(self)
        except AttributeError: pass #if parent is none, ignore.
        #ValueError for child not being in parent will still propagate
        self._parent = None

    def trim_children(self):
        """Trim and return a list of children."""
        child_list = list(self.children())
        for child in child_list:
            child.trim()
        return child_list

    def depth(self):
        """Find depth relative to full tree."""
        d = 0
        node = self
        while node.parent():
            node = node.parent()
            d += 1
        return d

    def route_to_root(self):
        """ Generate nodes ordered from self to root"""
        node = self
        yield node
        while node.parent():
            # create path to parent
            node = node.parent()
            yield node

    def route_from_root(self):
        """"Fake" generate nodes ordered from root to self."""
        for node in reversed(list(self.route_to_root())): yield node

### untested in unittests
    def route_to_ancestor(self, ancestor):
        """"Fake" generate nodes ordered from self to ancestor."""
        for node in reversed(list(self.route_from_ancestor(ancestor))):
            yield node

    def route_from_ancestor(self, ancestor):
        """Generate nodes ordered from ancestor to self."""
        node = ancestor
        yield node
        while node != self:
            node = node.parent()
            if node == None: raise ValueError('The node must be an ancestor of self.')
            yield node

    def traverse(self):
        """In-order generate all nodes in tree with self as root."""
        stack = deque()
        stack.append(self)
        while stack:
            node = stack.pop()
            #use reversed to get more logical human order on the stack
            for child in reversed(list(node.children())):
                stack.append(child)
            yield node

    def traverse_post_order(self):
        """Post-order "Fake" generate all nodes in tree with self as root."""
        ###is there a way to do this without making a full list? probably.
        for node in reversed(list(self.traverse())):
            yield node

    def leaves(self):
        """Generate all leaves of tree with self as root."""
        for node in self.traverse():
            if not list(node.children()): yield node

    def trim_dead_branch(self,
                         stop_data_key = None,
                         stop_data_value = None):
        """Trim up from leaf and return root of dead branch. Stop conditions:
            a)parent is non-degenerate
            b)parent has stop data
            c)parent is the full tree root
            
        """
        #make sure this is a leaf
        if list(self.children()):
            raise ValueError('Start node must be a leaf')
        #move up the branch until stop condition(s) met
        dead_node = self
        while dead_node.parent():
            parent = dead_node.parent()
            if len(list(parent.children())) > 1: break #parent is non-degenerate
            try: #parent has stop data
                if parent.data[stop_data_key] == stop_data_value: break 
            except KeyError: pass
            if not parent.parent(): break #parent is full tree root
            dead_node = parent
        dead_node.trim()
        return dead_node

    def degenerate_to_leaf(self, leaf):
        """Make tree degenerate from self down to leaf.

        arguments:
        leaf -- leaf SimpleNode connected to tree of self

        """
        #determine that there is a path before actually modifying the tree
        path = [leaf]
        current = leaf
        while current != self:
            try: path.append(current.parent())
            except AttributeError: raise ValueError('There is no vertical path'\
                                                    'between self and leaf')
            current = current.parent()
        #if a vertical path was found, make path degenerate
        #note: important to use trim so both connections are broken
        parent = path.pop()
        while list(parent.children()):
            protected_child = path.pop()
            children = list(parent.children())
            for child in children:
                if child != protected_child: child.trim()
            parent = protected_child

    def search(self, data_items):
        """Generate all matching nodes.

        arguments:
        data_items -- dict with key,value pairs to be checked for in tree

        """
        for node in self.traverse():
            for key, value in data_items.items():
                found = True
                try:
                    if node[key] != value:
                        found = False
                        break
                except KeyError:
                    found = False
                    break
            if found: yield node

    

def main():
    pass

if __name__ == '__main__':
    main()


    
