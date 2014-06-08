'''Unit test for autoconfig.py'''
import unittest

import autoconfig

known_data = {'basics': {'string': 'abc',
                         'integer': 123,
                         'float': 123.,
                         'boolean': True,
                         'none': None},
              'strings': {'multiline strings': ['a','b','c'],
                          'commalist strings': ['a','b','c'],
                          'multiline commalist strings': [['a','b','c'],
                                                          ['d','e','f'],
                                                          ['g','h','i']]},
              'integers': {'multiline integers': [1,22,333],
                           'commalist integers': [1,22,333],
                           'multiline commalist integers': [[1,22,333],
                                                            [4444,55555,6666],
                                                            [777,88,9]]},
              'floats': {'multiline floats': [1., 2.2, .333],
                         'commalist floats': [1., 2.2, .333],
                         'multiline commalist floats': [[1.,2.2,.333],
                                                        [4.444,55.555,666.6],
                                                        [777.,8.8,.9]]},
              'booleans': {'multiline booleans': [True,False,False],
                           'commalist booleans': [True,False,False],
                           'multiline commalist booleans': [[True,True,True],
                                                            [False,False,False],
                                                            [False,True,True]]},
              'nones': {'commalist nones': [None,None,None]}}
##              'gotchas': {'all or none': ['1','a']}}

### don't write a test for every piece of the code.
### write a test for each piece of behavior that should be expected to work
### probably best to focus on public methods first at least

class TestConstruction(unittest.TestCase):
    def setUp(self):
        global known_data
        self.ac_byfile = autoconfig.AutoConfig.from_file('autoconfig_test.ini',
                                                         interpret_data = True)
        
    def test_from_file(self):
        self.assertDictEqual(self.ac_byfile._base_data,known_data)

    def test_from_external(self):
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile)
        self.assertDictEqual(ac_byexternal._base_external._base_data,known_data)


class TestSections(unittest.TestCase):
    def setUp(self):
        global known_data
        self.known_sections = [s for s in known_data.keys()]
        self.ac_byfile = autoconfig.AutoConfig.from_file('autoconfig_test.ini')

    def test_Sections_from_file_fresh(self):
        '''Test Sections() with fresh file-based data.'''
        self.assertSameElements(list(self.ac_byfile.sections()),
                                self.known_sections)

    def test_Sections_from_file_with_overrides(self):
        '''Test Sections() with overrides on file-based data.'''
        self.ac_byfile.override('basics', 'integer', None)
        self.assertSameElements(list(self.ac_byfile.sections()),
                                self.known_sections)

    def test_Sections_from_external_fresh(self):
        '''Test Sections() with fresh external-based data.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile)
        self.assertSameElements(list(ac_byexternal.sections()),
                                self.known_sections)

    def test_Sections_from_external_with_overrides(self):
        '''Test Sections() with overrides on external-based data.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile)
        ac_byexternal.override('strings', 'multiline strings', None)
        self.assertSameElements(list(ac_byexternal.sections()),
                                self.known_sections)

    def test_Sections_with_new_key_override(self):
        '''Test Sections() with a new key override.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile,
                                                            allow_new_keys=True)
        ac_byexternal.override('new section', None, None)
        self.assertEqual(set(ac_byexternal.sections()) ^
                         set(self.known_sections),
                         set(['new section']))

class TestOptions(unittest.TestCase):
    def setUp(self):
        global known_data
        self.section  = 'floats'
        self.known_options = [o for o in known_data[self.section].keys()]
        self.ac_byfile = autoconfig.AutoConfig.from_file('autoconfig_test.ini')

    def test_Options_from_file_fresh(self):
        '''Test Options() with fresh file-based data.'''
        self.assertSameElements(list(self.ac_byfile.options(self.section)),
                                self.known_options)

    def test_Options_from_file_with_overrides(self):
        '''Test Options() with overrides on file-based data.'''
        self.ac_byfile.override(self.section, 'commalist floats', None)
        self.assertSameElements(list(self.ac_byfile.options(self.section)),
                                self.known_options)

    def test_Options_from_external_fresh(self):
        '''Test Options() with fresh external-based data.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile)
        self.assertSameElements(list(ac_byexternal.options(self.section)),
                                self.known_options)

    def test_Options_from_external_with_overrides(self):
        '''Test Options() with overrides on external-based data.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile)
        ac_byexternal.override(self.section, 'commalist floats', None)
        self.assertSameElements(list(ac_byexternal.options(self.section)),
                                self.known_options)

    def test_Options_with_new_key_override(self):
        '''Test Options() with a new key override.'''
        ac_byexternal = autoconfig.AutoConfig.from_external(self.ac_byfile,
                                                            allow_new_keys=True)
        ac_byexternal.override(self.section, 'new option', None)
        self.assertEqual(set(ac_byexternal.options(self.section)) ^
                         set(self.known_options),
                         set(['new option']))

class TestGet(unittest.TestCase):
    def setUp(self):
        global known_data
        self.ac_byfile = autoconfig.AutoConfig.from_file('autoconfig_test.ini',
                                                         interpret_data = True,
                                                         allow_new_keys = True)

    def test_get_fresh(self):
        for section, options in known_data.items():
            for option, value in options.items():
                self.assertEqual(self.ac_byfile.get(section,option),
                                 value)

    def test_get_with_overrides(self):
        self.ac_byfile.override('new section', 'new option', 'new value')
        self.assertEqual(self.ac_byfile.get('new section', 'new option'),
                         'new value')

class TestOverride(unittest.TestCase):
    def setUp(self):
        global known_data
        self.original_s = 'basics'
        self.original_o = 'float'
        self.new_s = 'new section'
        self.new_o = 'new option'
        self.new_v = 'new value'
        self.ac_byfile = autoconfig.AutoConfig.from_file('autoconfig_test.ini',
                                                         allow_new_keys = True)

    def test_override_section(self):
        self.ac_byfile.override(self.new_s, self.new_o, self.new_v)
        self.assertDictEqual(self.ac_byfile._override[self.new_s],
                             {self.new_o: self.new_v})

    def test_override_option(self):
        self.ac_byfile.override(self.original_s, self.new_o, self.new_v)
        self.assertDictEqual(self.ac_byfile._override[self.original_s],
                             {self.new_o: self.new_v})

    def test_override_override(self):
        self.ac_byfile.override(self.original_s, self.new_o, self.new_v)
        self.ac_byfile.override(self.original_s, self.new_o, 'new 2')
        self.assertDictEqual(self.ac_byfile._override[self.original_s],
                             {self.new_o: 'new 2'})


if __name__ == "__main__":
    try: unittest.main()
    except SystemExit: pass
