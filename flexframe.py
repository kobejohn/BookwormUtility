from itertools import chain
from copy import deepcopy


class FlexFrame:
    """Base class that allows objects to be placed in arbitrary positions
    One object per position that should implement:
        __eq__()

    """
    ######## Start Required Overrides ########
    def clone(self, should_include_positions = True,
              should_override_data = False, override_data_item = None,
              override_base_object = None):
        """Create a copy of self with position and optionally items

        Arguments:
        include_data_references -- include references to original items or not

        Required Override:
        This function is required by some other functions that assume this
        creates class-specific copies of an instance (i.e. not the base class)
        """
        if override_base_object:
            new_ff = override_base_object
            new_ff.clear_frame()
        else: new_ff = self._class(*self._dimensions,
                                   separators = self._separators)
        if should_include_positions:
            for item, position in self.nodes():
                if should_override_data: item = override_data_item
                new_ff.place(item, *position)
        return new_ff
    ######## End Required Overrides ##########
    ######## Start Optional Overrides ########
    def load_content(self, iterable_content):
        """ optional override, non-required function to load data conveniently
        """
        old_nodes = self._nodes
        self.clear_frame()
        try:
            for index, item in enumerate(iterable_content):
                self.place(item, index)
        except TypeError:
            print('content is not iterable: ', iterable_content)
            self._nodes = old_nodes

    def _serialize_positions(self,
                             dimension_sort_order = None, descending = False):
        """ optional override to provide meaningful order to serial positions
                -access _nodes directly, not through self iterator
                -called for every new iterator so be careful of performance
        """
        if dimension_sort_order:
            all_p = [position for position in self._nodes.keys()]
            current_sorts = [[position for position in self._nodes.keys()]]
            ################                  YYYYYYYUUUUUUUUUUCCCKKKK
            ################                

            ### instead of all this crap, implement >< and just use sort
            ### then get rid of dimension sort order strangeness
    


            
            ### need to try:except in case a sort_dimension is not sortable
            for sort_dimension in dimension_sort_order:
                # get unique set of sorted values for current sort dimension
                sorted_values =sorted(set([getattr(position, sort_dimension) for
                                        position in all_p]),
                                       reverse = descending)
                # for each sorted set in previous sort dimension,
                # further split the set for the next sort dimension
                next_sorts = []
                for current_sort in current_sorts:
                    for sorted_value in sorted_values:
                        next_sort = [position for position in current_sort if
                                     getattr(position, sort_dimension) == sorted_value]
                        next_sorts.append(next_sort)
                current_sorts = next_sorts
            for position in chain.from_iterable(current_sorts):
                yield position
        else:
            for position in self._nodes.keys():
                yield position

    def __repr__(self):
        """ optional override for string representation of FlexFrame
                -access _nodes through self iterator
                -by default sorts by all dimensions
        """
        text_list = []
        for item, position in self._internal_nodes(dimension_sort_order = \
                                                   self._dimensions):
            text_list.append(str(item))
        return ''.join(text_list)
    ######## End Optional Overrides ##########

    def __init__(self, *args, separators=None):
        """FlexFrame(dimension_name, dimension_name, ..., separators=[[before,after]])
        """
        self._class = FlexFrame
        self._dimensions = [dimension for dimension in args]
        self._separators = separators
        self.clear_frame()
        
    def _position_args_to_position(self, *args, **kwargs):
        if args: # priority to ordered position values
            dimension_values = [[self._dimensions[i],value] for
                                 i, value in enumerate(args)]
            return FlexPosition(*dimension_values,
                                separators = self._separators)
        ### handle other versions later after this works

    def clear_frame(self):
        self._nodes = {}

    ### really use this even though it's funky? 
    def look(self, *args, **kwargs):
        """ look(dimension_value, dimension_value, ...) -> object
        """
        position = self._position_args_to_position(*args, **kwargs)
        try: return self._nodes[position]
        except KeyError:
            raise KeyError('position doesn\'t exist in frame', position)
        
    def pickup(self, *args, **kwargs):
        """ pickup(dimension_value, dimension_value, ...) -> object
            removes an item from a position, but leaves the position
        """
        position = self._position_args_to_position(*args, **kwargs)
        try:
            content = self._nodes[position]
            self._nodes[position] = None
            return content
        except KeyError:
            raise KeyError('position doesn\'t exist in frame', position)

    def place(self, item, *args, **kwargs):
        """ place(content, dimension_value, dimension_value, ...)
            places an item in the frame (replaces any current item)
        """
        position = self._position_args_to_position(*args, **kwargs)
        self._nodes[position] = item

    def delete_position(self, *args, **kwargs):
        """ delete_position(dimension_value, dimension_value, ...)
            removes a position itself from frame including any item there
        """
        position = self._position_args_to_position(*args, **kwargs)
        try:
            del(self._nodes[position])
        except KeyError:
            raise KeyError('position doesn\'t exist in frame', position)

    def nodes(self, dimension_sort_order = None, descending = False):
        """ nodes([by_dimension, descending]) -> node iterator
            node iterator with an optional sort by a specific dimension
        """
        for item, position in self._internal_nodes(dimension_sort_order, descending):
            yield item, \
                  [getattr(position, dimension) for
                   dimension in self._dimensions]

    def _internal_nodes(self, dimension_sort_order = None, descending = False):
        for position in self._serialize_positions(dimension_sort_order, descending):
            item = self._nodes[position]
            yield item, position

    def __eq__(self, other):
        """ true if and only if:
                -positions are one to one
                -each position's objects are equal by their own __eq__
        """
        try:
            # test for one to one positions
            if self._nodes.keys() != other._nodes.keys():
                return False
            #test for each node's object being equal by self's object's __eq__
            for item, position in self._internal_nodes():
                if item != other._nodes[position]:
                    return False
        except: return False
        return True
    
    def __ne__(self, other):
        return not self.__eq__(other)

    def __sub__(self, other):
        """Find the difference between two FlexFrames.
        By using clone, this should return inherited version of FlexFrame.

        Conditions:
        Does not require same positions. Results will only have positions
        that exist in both self and other

        Returns:
        placed -- a cloned self with the self items that changed 
        pickedup -- a cloned self with the other items that changed
        
        """
        placed = self.clone(should_include_positions = False)
        pickedup = self.clone(should_include_positions = False)
        for self_item, position in self.nodes():
            try: other_item = other.look(*position)
            except KeyError: continue
            if self_item != other_item:
                placed.place(self_item, *position)
                pickedup.place(other_item, *position)
        return placed, pickedup

    def __contains__(self, item):
        for node_item, position in self._internal_nodes():
            if node_item == item:
                return True
        return False


### probably better to get rid of this? put functionality directly into FF?
class FlexPosition:
    """Base class for a discrete position defined by arbitrary dimensions.

    Required interface:
     _dimensions --
     _separators --
     __eq__() --
     __hash__() --

    """

    def __init__(self, *args, separators = None):
        """ FlexPosition([dimension_name,value],..., separators=[[before,after]])
            or FlexPosition(value,..., separators=[[before,after]])
        """
        self._dimensions = []
        for dimension, value in args:
            setattr(self, dimension, value)
            self._dimensions.append(dimension)
        self._separators = separators if separators else \
                           self._standard_separators(self._dimensions)

    ######## Start Optional Overrides ##########
    def __repr__(self):
        """ optional override to provide specialized string representation """
        string_list = []
        for i, dimension in enumerate(self._dimensions):
            before, after = self._separators[i]
            string_list.append(before)
            string_list.append(str(getattr(self, dimension)))
            string_list.append(after)
        return ''.join([string for string in string_list])
    ######## End Optional Overrides ##########

    def _key(self):
        """ create a hashable key of this position. """
        key_list = [getattr(self, dimension) for dimension in self._dimensions]
        return tuple(key_list)
    
    def __hash__(self):
        return hash(self._key())

    def __eq__(self, other):
        """ return True if and only if:
            the dimensions of both objects are equivalent
            and the values of the dimensions of both objects are equivalent
        """
        try:
            # test for one to one dimensions
            if self._dimensions != other._dimensions: return False
            #test for each dimension's value being equal by self's dimension's __eq__
            for dimension in self._dimensions:
                if getattr(self, dimension) != getattr(other, dimension):
                    return False
        except: return False
        return True

    def __ne__(self, other):
        return not self.__eq__(other)

    def _standard_separators(self, dimensions):
        separators = []
        last_index = len(dimensions) - 1
        for i, d in enumerate(dimensions):
            before = '(' if i==0 else ','
            after = ')' if i==last_index else ''
            separators.append([before, after])
        return separators








class FlexGrid(FlexFrame):
    """Specialized FlexFrame that uses lists instead of dicts for the case
    that dimensions can be positive integer values and all rectangular
    spaces between provided values are assumed to exist with value None.

    """
    def __init__(self, *args, separators = None,
                 initial_sizes, empty_object = None):
        """Create a FlexGrid.

        arguments:
        *args - dimension_name, dimension_name, ...
        initial_sizes - fixed size of each dimensions [size, size, ...]

        optional arguments:
        separators - text to use in repr - [[before,after]...]
        empty_object - object to place in "empty" spaces on the grid

        """
        self._empty_object = empty_object
        self._initial_sizes = initial_sizes
        super().__init__(*args, separators = separators)

    def _create_grid(self, *args):
        """Create the grid lists based on args as dimension sizes."""
        args = list(args)
        last_size = args.pop()
        nodes = [self._empty_object] * last_size
        for size in reversed(args):
            nodes = [deepcopy(nodes) for i in range(size)]
        return nodes
        
    def clear_frame(self):
        """Clear all positions and therefore content from the frame."""
        self._nodes = self._create_grid(*self._initial_sizes)

    def _internal_nodes(self, dimension_sort_order = None):
        """Yield all nodes in standard list order. I.e. sort order is ignored"""
        # content items are all in the last dimension
        # iteratively (i.e. not recursively) go through all dimensions of _nodes
        d_count = len(self._dimensions)
        position = [0] * d_count
        d_iterators = [iter(self._nodes)]
        d_index = 1
        while d_iterators:
            position = list(position) #copy values
            #get the next object. either dimension or item
            try: next_object = d_iterators[-1].__next__()
            except StopIteration: #finished all items of a dimension
                d_index -= 1 #go back one dimension when finished
                position[d_index] = 0 #reset completed dimension
                position[d_index-1] += 1 #increment previous dimension
                del(d_iterators[-1]) #remove the spent iterator
                continue
            #treat as dimension iterables up to dimension count
            #note: can't use try/except since item could be iterable
            if d_index < d_count:
                d_index += 1
                d_iterators.append(iter(next_object))
            #after dimension count, yield the data item if not empty
            else:
                if next_object != self._empty_object:
                    yield next_object, position
                position[d_index-1] += 1

    def __repr__(self):
        """ Override to print self._empty_object items as empty spaces."""
        text_list = []
        for item, position in self._internal_nodes():
            if item == self._empty_object: item = ' '
            text_list.append(str(item))
        return ''.join(text_list)

    def look(self, *args):
        """ look(dimension_value, dimension_value, ...) -> object
        """
        position = [None]*len(self._dimensions)
        item = self._nodes
        for i, coordinate in enumerate(args):
            try: item = item[coordinate]
            except IndexError:
                raise ValueError('Position doesn\'t exist in frame.')
        return item

    def pickup(self, *args):
        """ pickup(dimension_value, dimension_value, ...) -> object
            removes an item from a position, but leaves the position
        """
        item = self.look(*args)
        self.place(self._empty_object, *args)
        return item

    def place(self, item, *args):
        """ place(content, dimension_value, dimension_value, ...)
            places an item in the frame (replaces any current item)
        """
        position = list(args) #in case position is provided as a tuple
        last_coordinate = position.pop()
        node = self._nodes
        for i, coordinate in enumerate(position):
            try: node = node[coordinate]
            except IndexError:
                raise ValueError('Position doesn\'t exist in frame.')
        try: node[last_coordinate] = item
        except IndexError: raise ValueError('Position doesn\'t exist in frame.')

    def delete_position(self, *args):
        """Replace the item at position with the empty object."""
        self.place(self._empty_object, *args)

    def nodes(self, dimension_sort_order = None, descending = False):
        """ nodes([by_dimension, descending]) -> node iterator
            node iterator with an optional sort by a specific dimension
        """
        for item, position in self._internal_nodes(dimension_sort_order):
            yield item, position

    def __eq__(self, other):
        """ true if and only if:
                -dimensions are equivalent
                -positions are one to one
                -each position's objects are equal by their own __eq__
        """
        try:
            if self._dimensions != other._dimensions: return False
        except AttributeError: return False
        try:
            if self._nodes != other._nodes: return False
        except AttributeError: return False
        return True
