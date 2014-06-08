from collections import deque
from collections import OrderedDict
from itertools import chain
import pickle

import simpletree
import wordlist

class AnagramSolver:
    '''
    Maintains an internal wordlist (parsed for search speed... I think)
    Given a set of tiles, each with one or more letters,
    provides a list of words built by tiles and sorted by score
        Provided tiles must have an attribute 'letters'
    '''
    def __init__(self, min_letters = 1, max_letters = None):
##        ### this code makes the pickle in the module path
##        ### instead of caller path
##        if '__file__' in globals(): #path to this source file
##            this_dir = os.path.abspath(os.path.dirname(__file__))
##        else: #relative path when running IDLE, etc.
##            this_dir = ''
##        pickle_path = os.path.join(this_dir, 'wordtree.pickle')
        try: #try to load word tree from pickle to save lots of processing
            f = open('wordtree.pickle', 'rb')
            word_root = pickle.load(f)
        except (IOError, EOFError, pickle.UnpicklingError):
            print('Error loading word tree pickle. Creating a new one.')
            # create new word tree if pickle not available
            #filtering at the beginning by length reduces the size of the index
            words = wordlist.WordList().filter_by(min_letters, max_letters)
            word_root = self._parse_words_to_tree(words)
            f = open('wordtree.pickle', 'wb')
            pickle.dump(word_root, f, pickle.HIGHEST_PROTOCOL)
        self._word_root = word_root

    def best_words(self, free_tiles, fixed_tiles = None, wrong_pos_tiles = None,
                   unique_words = True, list_limit = None, low_points = False,
                   min_tiles = 1, max_tiles = None):
        '''
        tiles is a list of Tile objects (has letters, unique_key, points())
        '''
        tile_root = self._build_tile_tree(free_tiles, fixed_tiles,
                                          wrong_pos_tiles, min_tiles, max_tiles)
        all_words = self._find_tile_words(tile_root, min_tiles, max_tiles) #list of tile sequences
        # sort list by total score for each tile sequence
        sorted_words = sorted(all_words, key = lambda sequence: \
                              sum([tile.points() for tile in sequence]),
                              reverse = not low_points)
        if unique_words:
            sorted_words = self._unique_words(sorted_words)
        if list_limit:
            if list_limit >= 0:
                sorted_words = sorted_words[0:list_limit]
        return sorted_words

    def _unique_words(self, words):
        ' words must be a list of tile sequences(lists) '
        ' maintains sorting '
        ### replace this with a set filter
        unique_words = OrderedDict()
        for word in reversed(words):
            string = ''
            for tile in word:
                string += tile.letters
            unique_words[string] = word
        return [unique_words[string] for string in reversed(unique_words)]

    ### build tree may be doing too many things during construction.
    ### simplify and process later?
    def _build_tile_tree(self, free_tiles, fixed_tiles, wrong_pos_tiles,
                         min_tiles, max_tiles):
        q = deque()
        tile_root = simpletree.TreeNode()
        tile_root['tile'] = None
        tile_root['is a word'] = False
        tile_node = tile_root
        letter_node = self._word_root
        package = [letter_node, tile_node, free_tiles]
        q.append(package) #initialize queue with both roots and all tiles
        # continue processing qualifying nodes for longer words
        while q:
            letter_node, tile_node, free_tiles = q.pop()
            duplicate_test = []
            depth = tile_node.depth()
            # if this depth should be a fixed tile, override available tiles
            try: fixed_tile = fixed_tiles[depth]
            except (IndexError, TypeError):  fixed_tile = None
            if fixed_tile:
                tiles = [fixed_tile]
                fixed = True
            else:
                tiles = free_tiles
                fixed = False
            for tile in tiles:
                #skip if duplicate tile
                if tile in duplicate_test: continue
                #skip if this is a disallowed position
                try:
                    if tile.letters in [wrong_tile.letters for wrong_tile in
                                        wrong_pos_tiles[depth]]: continue
                except (TypeError, IndexError): pass
                #look for a match for this tile's letters in letter tree
                new_letter_node = letter_node
                for letter in tile.letters:
                    try:
                        new_letter_node = \
                           list(new_letter_node.children_by_data('letter',
                                                            letter.lower()))[0]
                    except IndexError:
                        new_letter_node = None
                        break # stop when leaf letters reached
                if new_letter_node == None: continue #continue to next tile
                # add a new tile node
                new_tile_node = simpletree.TreeNode()
                new_tile_node['tile'] = tile
                tile_node.graft(new_tile_node)
                # mark as a word if it qualifies
                mark_word = False
                if new_letter_node['is a word']:
                    mark_word = True
                    if min_tiles:
                        if depth + 1 < min_tiles:
                            mark_word = False
                    if max_tiles:
                        if depth + 1 > max_tiles: mark_word = False
                    word = self._node_to_word(new_tile_node)
                    if wrong_pos_tiles:
                        for wp_tile in chain.from_iterable(wrong_pos_tiles):
                            if wp_tile:
##                                #### this needs to count the tiles not just check in
##                                #### e.g. one gold A and one silver A --> in passes
##                                #### but actually 2 A's are necessary in the final word
##                                #### but... a silver A that has later become
##                                #### a gold A shouldn't be counted twice....?
##                                #### arrgh. write out some examples to figure
##                                #### what counts need to be compared
##                                #### eliminate the number of silver letters
##                                #### that have become gold letters later?
##                                #### probably need to fix the incoming information
##                                #### from bookworm AND fix here to counts
##                                len([test_tile for test_tile in 
                                if wp_tile.letters not in \
                                   [word_tile.letters for word_tile in word]:
                                    mark_word = False
                new_tile_node['is a word'] = mark_word
                #mark match in duplicate_test
                duplicate_test.append(tile)
                # make a new tile list
                new_tiles = [new_tile for new_tile in free_tiles]
                if not fixed: #remove current tile if working with free_tiles
                    new_tiles.remove(tile)
                # queue package if tiles remaining and under max_tiles
                make_package = True
                try: new_tiles[0] #at least 1 tile
                except IndexError: make_package = False
                try:
                    if depth >= max_tiles:
                        make_package = False
                except TypeError: pass
                if make_package:
                    package = [new_letter_node, new_tile_node, new_tiles]
                    q.append(package)
        # trim any dead ends (could do during creation but gave me a headache)
        for leaf in tile_root.leaves():
            if leaf['is a word'] == True: continue
            leaf.trim_dead_branch(stop_data_key = 'is a word',
                                  stop_data_value = True)
        return tile_root

    def _find_tile_words(self, tile_root, min_tiles, max_tiles):
        words = []
        for word_node in tile_root.traverse():
            word = self._node_to_word(word_node)
            num_tiles = len(word)
            add_word = True
            if not word_node['is a word']:
                add_word = False
            try:
                if num_tiles < min_tiles: add_word = False
            except TypeError: pass
            try:
                if num_tiles > max_tiles: add_word = False
            except TypeError: pass
            if add_word: words.append(word)
        return words

    def _node_to_word(self, tile_node):
        return [node['tile'] for node in tile_node.route_from_root() if
                node['tile']] #exclude root

    def _parse_words_to_tree(self, words):
        ### shouldn't this be in word list? ###
        '''
        each letter node contains:
            - letter (one character string)
            - is a word (boolean)
            - next_letters (dict)
        '''
        root = simpletree.TreeNode()
        root['letter'] = None
        root['is a word'] = False
        for word in words:
            current = root #start spelling new word at root
            for letter in word:
                try: #found letter. move ahead
                    current = \
                        list(current.children_by_data('letter', letter))[0]
                    continue
                except IndexError: #didn't find letter. crate it.
                    new = simpletree.TreeNode()
                    new['letter'] = letter
                    new['is a word'] = False
                    current.graft(new)
                    current = new
            current['is a word'] = True
        return root

def main():
    import tile

    solver = AnagramSolver(min_letters = 2, max_letters = 20) #18 allows for 3x qu
    free_tiles = [tile.Tile(letters = alpha) for alpha in 'techerasdfasdf']
    t = tile.Tile(letters = 't')
    a = tile.Tile(letters = 'a')
    fixed_tiles = [None,None,a]
    wrong_pos_tiles = [[],[t]]
    best = solver.best_words(free_tiles, fixed_tiles, wrong_pos_tiles,
                             min_tiles = 7, max_tiles = 7)
    for word in best:
        for tile_ in word:
            print(tile_.letters, end='')
        print('')

    go = True
    while go:
        user_input = input('Letters or ''Q'' (''Qu'' already included): ')
        if user_input.upper() == 'Q':
            go = False
        elif not user_input.isalpha():
            continue
        else:
            tiles = [tile.Tile(letters = letter) for letter in user_input]
            tiles.append(tile.Tile(letters = 'qu'))
            best = solver.best_words(tiles, list_limit = 10)
            for word in best:
                for tile_ in word:
                    print(tile_.letters, end = '')
                print('')

            

if __name__ == '__main__':
    main()
