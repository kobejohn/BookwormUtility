#attribute 12dicts appropriately

#make dictionary loading choice


class WordList:
    '''
    Provides subsets of words from an internal dictionary of words
    Internal Dictionary based on 12dicts
    '''

    def __init__(self):
        self._words = self._load_words()

    def __iter__(self):
        for word in self.filter_by():
            yield word

    def filter_by(self, min_length = 1, max_length = None,
                  plural_uncountables = True):
        for word in self._words:
            #filter plural uncountables
            if  (plural_uncountables == False) and ('%' in word):
                continue
            word = word.replace('%','')
            
            #filter by length
            length = len(word)
            if min_length and (length < min_length):
                continue
            if max_length and (max_length < length):
                continue
            #include word if not filtered already
            yield word

    def _load_words(self):
        import os

        if '__file__' in globals(): #path to this source file
            this_dir = os.path.abspath(os.path.dirname(__file__))
        else: #relative path when running IDLE, etc.
            this_dir = ''
        file_path = os.path.join(this_dir, 'dictionaries\\2of12inf.txt')
##        file_path = os.path.join(this_dir, 'dictionaries\\test.txt')
        f = open(file_path)
        return f.read().splitlines()
                




def main():
    words = WordList()

    print('***********Filtered to 1')
    for word in words.filter_by(min_length = 1, max_length = 1):
        print(word)

    print('***********Filtered 18 to 20')
    for word in words.filter_by(min_length = 18, max_length = 20):
        print(word)
    
    print('***********Filtered 20 to unlimited')
    for word in words.filter_by(min_length = 20):
        print(word)

    print('***********Filtered 18 to 18 and exclude plural uncountable')
    for word in words.filter_by(min_length = 18, max_length = 18,
                                plural_uncountables = False):
        print(word)


if __name__ == '__main__':
    main()
