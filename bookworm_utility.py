import os
from collections import OrderedDict
from time import sleep
from functools import partial

import autoconfig
import image_to_data
import anagram_solver
import tile
import flexframe
import simpleui

class BookwormUtility:
    '''
    Provides lists of words based on the letter tiles provided in the game
        -Uses a simple UI utility to provide an interface
        -Grabs game data through screenshots
    '''
    def __init__(self):
        self._ac = autoconfig.AutoConfig.from_file('config.ini',
                                                  interpret_data = True)
        ''' create the image to data objects '''
        template_path = self._ac.get('templates','letters path')
        letters = self._get_letter_templates(path = template_path)
        ### can get rid of the scale_h junk when scale invariant implemented
        scale_h = self._ac.get('templates','letter parent height')
        self._screen_to_letters = image_to_data.ImageToData(\
            templates_and_data = letters, method = 'grayscale correlation',
            crop_to_resolution = True, crop_to_4to3_aspect = True,
            shrink_to_height = scale_h)

        template_path = self._ac.get('templates','statuses path')
        statuses = self._get_status_templates(path = template_path)
        self._screen_to_status = image_to_data.ImageToData(\
            templates_and_data = statuses, method = 'rgb correlation',
            crop_to_resolution = True, crop_to_4to3_aspect = True,
            shrink_to_height = scale_h)

        ''' anagram solver takes time to load, so do it on startup '''
        ### change to a function
        self._anagram = anagram_solver.AnagramSolver(
                          min_letters = self._ac.get('anagram','min letters'),
                          max_letters = self._ac.get('anagram','max letters'))
        
        ''' calculate and store grid regions '''
        grids = {} #OrderedDict()
        self._grids = grids
        for name in [section for section in self._ac.sections() if
                     'grid' in section]:
            grids[name] = self._calc_grid_percents(
                                        self._ac.get(name,'screen_h'),
                                        self._ac.get(name,'screen_w'),
                                        self._ac.get(name,'grid_top'),
                                        self._ac.get(name,'grid_left'),
                                        self._ac.get(name,'step'),
                                        self._ac.get(name,'padding'),
                                        self._ac.get(name,'rows'),
                                        self._ac.get(name,'columns'))

        ''' create the ui '''
        ui = simpleui.SimpleUI(exit, hide = True)
        self._ui = ui
        ui.add_frame('frame1')
        ui.add_button('button1','Main Grid', self.main_words, 'frame1')
        ui.add_button('button2','Letter Rip', self.letterrip_words, 'frame1')
        ui.add_button('button3','Link n Spell', self.linknspell_words, 'frame1')
        ui.add_button('button4','Word Master', self.wordmaster_words, 'frame1')
        callback = partial(self.main_words, **{'debug_path':
                              'test/locked crystal emerald (border).png'})
        ui.add_button('button5', 'Debug Main', callback, 'frame1')
        callback = partial(self.letterrip_words, **{'debug_path':
                              'test/letter rip (border).png'})
        ui.add_button('button6', 'Debug Letter Rip', callback, 'frame1')
        callback = partial(self.linknspell_words, **{'debug_path':
                              'test/linknspell (border).png'})
        ui.add_button('button7', 'Debug Link N Spell', callback, 'frame1')
        callback = partial(self.wordmaster_words, **{'debug_path':
                              'test/word master 2 (border).png'})
        ui.add_button('button8', 'Debug Word Master', callback, 'frame1')        
        ui.add_textout('textout1', 'frame1')
        ui.show()

    def main_words(self, send_to_ui = True, num_words = None,
                   debug_path = None):
        best_words = self._get_words('main grid', num_words, debug_path)
        output_text = self._build_result_text(best_words)
        if send_to_ui: self._send_text_to_ui(output_text)
        
    def letterrip_words(self, send_to_ui = True, num_words = None,
                        debug_path = None):
        if not num_words: num_words = self._ac.get('output','num solutions')
        tile_grid = self._get_tile_grid('letter rip grid', debug_path)
        print(tile_grid) ################## DEBUG
        tiles = [tile for tile, position in tile_grid.nodes()]
        best_words = self._anagram.best_words(tiles, unique_words = True,
                                              low_points = False,
                                              list_limit = num_words,
                                              min_tiles = 3)
        output_text = self._build_result_text(best_words)
        if send_to_ui: self._send_text_to_ui(output_text)
        
    def linknspell_words(self, send_to_ui = True, num_words = None,
                         debug_path = None):
        ### still getting some unnecessary words early in the list and
        ### more words than necessary
        tile_grid = self._get_tile_grid('link n spell grid', debug_path)
        print(tile_grid) ################## DEBUG
        all_tiles = [tile for tile, position in tile_grid.nodes()]
        for tile in all_tiles:
            tile.status = 'used count 0'
        final_words = []
        words = self._anagram.best_words(all_tiles, unique_words = True)
        # process the words list until all tiles fully used or other condition
        while 1:
            best_word_points = -99999 #ugh. I don't know a better way
            best_word = None
            best_tile_points = -99999 #ugh. I don't know a better way
            for word in words:
                word_points = 0
                for tile in word:
                    tile_points = -1 if tile.status == 'used count 3' else 1
                    word_points += tile_points
                    if tile_points > best_tile_points:
                        best_tile_points = tile_points
                if word_points > best_word_points:
                    best_word_points = word_points
                    best_word = word
            #stop conditions
            if 0 == len(words):
                break #stop if no more words left (should never happen?)
            if 0 == len([tile for tile in all_tiles if
                         tile.status != 'used count 3']):
                break #stop if all tiles done
            if best_tile_points <= 0:
                break #stop if no useful tiles in words
            #update based on best choice if still looking for more words
            final_words.append(best_word)
            words.remove(best_word)
            for tile in best_word:
                tile.status = {'used count 0':'used count 1',
                               'used count 1':'used count 2',
                               'used count 2':'used count 3',
                               'used count 3':'used count 3'}[tile.status]
        output_text = self._build_result_text(final_words)
        if send_to_ui: self._send_text_to_ui(output_text)

    def wordmaster_words(self, send_to_ui = True, num_words = None,
                         debug_path = None):
        ### should give priority to vowels and deprioritize repeated letters?
        ### override letter points in config?
        if not num_words: num_words = self._ac.get('output','num solutions')
        free_tiles, fixed_tiles, wrong_position_tiles = \
                                       self._get_wordmaster_status(debug_path)
        print('fixed: ', fixed_tiles) ######################### DEBUG
        print('move: ', wrong_position_tiles) ######################### DEBUG
        best_words = reversed(self._anagram.best_words(free_tiles, fixed_tiles,
                                              wrong_position_tiles,
                                              max_tiles = 5, min_tiles = 5,
                                              list_limit = num_words))
        output_text = self._build_result_text(best_words)
        if send_to_ui: self._send_text_to_ui(output_text)
        return output_text

    def _get_wordmaster_status(self, debug_path):
        # gather information from the solution area
        solution_grid = self._get_tile_grid('word master solution grid',
                                            debug_path)
        print(solution_grid)
        fixed_tiles = [None]*5
        incorrect_tiles = []
        suggestion_tile = solution_grid.look(0,0)
        if suggestion_tile.status != 'empty':
            fixed_tiles[0] = suggestion_tile
        wrong_position_tiles = [[],[],[],[],[]]
        for tile, [row,col] in solution_grid.nodes():
            if tile.status == 'gold':
                fixed_tiles[col] = tile
            if tile.status == 'incorrect':
                #gold or silver letters that also fail aren't disabled automatically
                incorrect_tiles.append(tile)
            if tile.status == 'silver':
                if tile not in wrong_position_tiles[col]:
                    wrong_position_tiles[col].append(tile)

        # gather information from the available tile area
        tile_grid = self._get_tile_grid('word master tiles grid', debug_path)
##        print(sorted([tile.letters for tile, position in tile_grid.nodes()]))
        max_repeats = max(0,
                          5 - (len([tiles for tiles in wrong_position_tiles if tiles])
                           + len([tile for tile in fixed_tiles if tile])))
        free_tiles = []
        for tile, position in tile_grid.nodes():
            if tile.status == 'disabled': continue
            if tile.letters in [it.letters for it in incorrect_tiles]: continue
            free_tiles.extend([tile] * (1 + max_repeats))
        return free_tiles, fixed_tiles, wrong_position_tiles

    def _get_words(self, grid_name, num_words = None, debug_path = None):
        if not num_words:
            num_words = self._ac.get('output','num solutions')
        tile_grid = self._get_tile_grid(grid_name, debug_path)
        print('-' * 19)
        print(tile_grid)
        tiles = [tile for tile, position in tile_grid.nodes() if
                 tile.status != 'locked']
        best_words = self._anagram.best_words(tiles, unique_words = True,
                                              list_limit = num_words)
        return best_words

    def _build_result_text(self, tile_words):
        output_list = []
        for word in tile_words:
            output_list.append(self.tiles_to_string(word) + '\n')
        output_text = ''.join(output_list)
        return output_text

    def _send_text_to_ui(self, output_text):
        self._ui.change_text('textout1', output_text)

    def _get_tile_grid(self, grid_name, debug_path):
        letter_grid = self._identify_letters(grid_name, debug_path)
        status_grid = self._identify_statuses(grid_name, debug_path)
        tile_grid = BookwormGrid()
        for tile, [row, col] in letter_grid.nodes():
            letters = letter_grid.look(row, col).letters
            status = status_grid.look(row, col).status
            multipliers = {option: self._ac.get('status multipliers',option) for option in self._ac.options('status multipliers')}
            points = {option: self._ac.get('letter points',option) for option in self._ac.options('letter points')}
            tile = BookwormTile(letters, status, multipliers, points)
            tile_grid.place(tile, row, col)
        return tile_grid

    def _identify_letters(self, grid_name, debug_path = None):
        window_title = self._ac.get('game','window title')
        grid = self._grids[grid_name]
        if debug_path:
            window_title = debug_path
        return self._screen_to_letters.get_data(window_title,
                                                pcnt_regions = grid)

    def _identify_statuses(self, grid_name, debug_path = None):
        window_title = self._ac.get('game','window title')
        grid = self._grids[grid_name]
        ### can get rid of the scale_h junk when scale invariant implemented
        scale_h = self._ac.get('templates','status parent height')
        if debug_path:
            window_title = debug_path
        return self._screen_to_status.get_data(window_title,
                                               pcnt_regions = grid)
        
    def _calc_grid_percents(self, screen_h, screen_w, grid_top, grid_left, step,
                            padding, rows, columns):
        ### adjust all this to use BookwormGrid
        p_grid = BookwormGrid()                                    
        for row_index, y in enumerate(range(grid_top, grid_top + step*(rows-1) + 1, step)):
            for col_index, x in enumerate(range(grid_left, grid_left + step*(columns-1) + 1, step)):
                screen_percents = {'top':100*(y + padding)/screen_h,
                                   'left':100*(x + padding)/screen_w,
                                   'bottom':100*(y+step)/screen_h,
                                   'right':100*(x+step)/screen_w}
                p_grid.place(screen_percents, row_index, col_index)
        return p_grid

    def tiles_to_string(self, word, show_status = False, show_points = False):
        string = []
        points = 0
        for tile in word:
            string.append(tile.letters.lower())
            if show_status and (tile.status != 'normal'):
                string.append('(')
                string.append(tile.status[0])
                string.append(') ')
            points += tile.points()
        result = ''.join(string)
        if show_points:
            result = string.strip() + '  ' + points
        return result

    def _get_letter_templates(self, path):
        td = {}
        for index, file in enumerate([f for f in os.listdir(path) if
                                      os.path.isfile(os.path.join(path,f))]):
            f_name = os.path.splitext(file)[0] #just file name
            if f_name == 'empty':
                f_name = ''
            tile = BookwormTile(f_name, '', None, None)
            td[index] = {'source':os.path.join(path,file),
                         'output_data':tile} 
        return td

    def _get_status_templates(self, path):
        td = {}
        for index, file in enumerate([f for f in os.listdir(path) if
                                      os.path.isfile(os.path.join(path,f))]):
            f_name = os.path.splitext(file)[0] #just file name
            tile = BookwormTile('', f_name, None, None)
            td[index] = {'source':os.path.join(path,file),
                         'output_data':tile} 
        return td

    def run_callbacks(self):
        self._ui.run_external_callbacks()

    def ui_is_running(self):
        return self._ui.is_running()



class BookwormGrid(flexframe.FlexFrame):
    def __repr__(self):
        str_list = []
        current_row = 0
        for tile, [row, col] in self.nodes(dimension_sort_order = ['row','col']):
            if row != current_row:
                str_list.append('\n')
            str_list.append(str(tile))
            str_list.append(' ')
            current_row = row
        return ''.join(str_list)

    def __init__(self):
        super().__init__('row','col')

class BookwormTile(tile.Tile):
    def __init__(self, letters, status,
                 status_multipliers, letter_points):
        attributes = {'letters': letters,
                      'status': status}
        super().__init__(**attributes)
        # these don't represent the identity of a tile so are not included
        # in the fundamental attributes (e.g. not included in equivalence)
        self._status_multipliers = status_multipliers
        self._letter_points = letter_points

    def __repr__(self):
        str_list = []
        str_list.append(self.letters)
        ### these values should be in config
        try: str_list.append({'normal':   '   ',
                              'smashed':  '(s)',
                              'locked':   '(l)',
                              'plagued':  '(p)',
                              'amethyst': '(a)',
                              'crystal':  '(c)',
                              'diamond':  '(d)',
                              'emerald':  '(e)',
                              'garnet':   '(g)',
                              'ruby':     '(r)',
                              'sapphire': '(h)',
                              'disabled': '(x)',
                              'incorrect':'(i)',
                              'gold':     '(o)',
                              'silver':   '(v)',
                              'empty':    '   ',
                              'used count 0':'(0)',
                              'used count 1':'(1)',
                              'used count 2':'(2)',
                              'used count 3':'(3)'}[self.status])
        except KeyError: str_list.append('   ')
        str_list.append(' ' * (2 - len(self.letters))) #spacing for aligned display with "Qu"
        return ''.join(str_list)
        
##    def __eq__(self, other):
##        try:
##            if self.status != other.status:
##                return False
##        except:
##            return False
##        return super().__eq__(other)
##
##    def __ne__(self, other):
##        return not __eq__(other)

    def points(self):
        if self.letters in self._letter_points:
            return (self._letter_points[self.letters] *
                    self._status_multipliers[self.status])
        else:
            return (sum([self._letter_points[letter.lower()] for letter in self.letters]) *
                    self._status_multipliers[self.status])


def main():
    bu = BookwormUtility()
    while bu.ui_is_running():
        bu.run_callbacks()
        sleep(.1)
    

if __name__ == '__main__':
    main()
