class Tile:
    """Provides convenient encapsulation of a game tile's attributes.
    Can be used to dynamically create any type of tile
    Can be inherited to provide a fixed set of attributes

    public methods:
    points()

    implemented operators:
    __eq__
    __ne__
    __repr__
    

    instance variables:
    based on the arguments provided to constructor

    """
    
    def __init__(self, **kwargs):
        """Create a Tile with given arguments as attributes/values.

        **kwargs:
        attribute_name = value, attribute_name = value, ...
        attribute_name -- string identifying an attribute of the tile
        value -- the value for the attribute

        """
        self._attributes = []
        for attribute, value in kwargs.items():
            self._attributes.append(attribute)
            setattr(self, attribute, value)

    def points(self):
        """Return 1 by default. Override can calculate points dynamically."""
        return 1

    def __eq__(self, other):
        """Compare based on all attributes, but not on points function.

        other -- has at least same attributes as self

        """
        try:
            for attribute in self._attributes:
                if getattr(self, attribute) != getattr(other, attribute):
                    return False
        except AttributeError: return False
##            raise AttributeError('equivalence attribute missing: ', attribute)
        return True

    def __ne__(self, other):
        """Negate __eq__."""
        return not self.__eq__(other)

    def __repr__(self):
        """Provide readable string representing the tile."""
        string_list = []
        for attribute in self._attributes:
            string_list.extend([attribute, ': ', getattr(self, attribute)])
        return ''.join(string_list)

    def _key(self):
        """ create a hashable key of this position. """
        key_list = [getattr(self, attribute) for attribute in self._attributes]
        return tuple(key_list)
    
    def __hash__(self):
        return hash(self._key())
        
