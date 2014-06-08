### interpretation currently allows for mixed types within same option.



class AutoConfig:
    """Convenient replacement for ConfigParser
    Runtime Overrides -- easy runtime new or override configuration values
    Flexible Base -- Base configuration on a file or another AutoConfig

    public methods:
    get()
    set_()
    sections()
    options()

    """
    def __init__(self, allow_new_keys):
        """Use one of the classmethod factories to construct AutoConfig.

        Arguments:
        allow_new_keys -- allow creation of new runtime sections/options
        
        """
        self._allow_new_keys = allow_new_keys
        self._override = {}

    @classmethod
    def from_file(cls, path, allow_new_keys = False, interpret_data = True):
        """Construct AutoConfig from a file.

        Arguments:
        path -- a path to a config file

        Keyword Arguments:
        allow_new_keys -- allow creation of new runtime sections/options
        interpret_data -- try to interpret values read from the file

        """
        obj = cls(allow_new_keys)
        obj._interpret_data = interpret_data
        obj._base_data = obj._parse_config_file(path)
        return obj

    @classmethod
    def from_external(cls, ac, allow_new_keys = False):
        """Construct AutoConfig based on an external AutoConfig.

        Arguments:
        ac -- the base external AutoConfig

        Keyword Arguments:
        allow_new_keys -- allow creation of new runtime sections/options

        """
        obj = cls(allow_new_keys)
        obj._base_external = ac
        return obj

    def get(self, section, option):
        """Get value associated with section and option.

        Arguments:
        section -- string identifying a [section]
        option -- string identifying an option within the section

        Returns: value associated with section and option with priority:
        runtime override > external or local base configuration

        """
        #try to return runtime override data first
        try: return self._override[section][option]
        except KeyError: pass
        
        #try to return base data (from external autoconfig)
        try: return self._base_external.get(section, option)
        except (AttributeError): pass
        
        #return base data (from local data) (exception if keys don't exist)
        return self._base_data[section][option]

    def override(self, section, option, value):
        """Set a runtime override value for section, option.

        Arguments:
        section -- string identifying a [section]
        option -- string identifying an option within section
        value -- override value to associate with section and option

        Affected By:
        self._allow_new_keys -- allow or disallow addition of new keys

        """
        e_message = 'section and/or option do not exist in the' \
                    'base and addition of new keys is disabled: '
        exists = (section in self.sections()) and \
                 (option in self.options(section))
        #stop if the keys don't exist and new ones are not allowed
        if not exists and not self._allow_new_keys:
            raise KeyError(e_message, section, option)
        #otherwise add/overwrite override
        try: self._override[section][option] = value
        except KeyError: self._override[section] = {option:value}

    def sections(self):
        """Yield all sections that exist in the base or override."""
        #get override sections
        override_sections = self._override.keys()

        #get base sections from external
        try: base_sections = self._base_external.sections()
        except AttributeError:
            #not external so assume base data available
            base_sections = self._base_data.keys()
        for section in set(override_sections) | set(base_sections):
            yield section

    def options(self, section):
        """Yield all section->options that exist in the base or override."""
        #get override options
        try: override_options = self._override[section]
        except KeyError: override_options = []
        #get base options from external
        try: base_options = self._base_external.options(section)
        except AttributeError:
            #not external so assume base data available
            base_options = self._base_data[section].keys()
        for option in set(override_options) | set(base_options):
            yield option

    def _parse_config_file(self, config_path):
        """Parse and optionally interpret all values in a config file.

        Arguments:
        config_path -- path to a ConfigParser readable file

        Returns:
        {section: {option: value}}

        """
        import configparser

        cp = configparser.ConfigParser()
        cp.read(config_path)
        config = {section: {option: self._parse_option(cp.get(section, option))
                            for option in cp.options(section)} for
                  section in cp.sections()}
        return config

    def _parse_option(self, option_text):
        """Further parse the original ConfigParser text.

        Arguments:
        option_text -- the standard text returned from ConfigParser.get()

        """
        option_value = []
        option_text = option_text.strip()
        lines = option_text.splitlines()
        if lines == []: return self._interpret('') #special case :(
        #treat each line as a list element for this option's value
        for line in option_text.splitlines():
            #assume commas indicate this line has a list of values
            line_value = [self._interpret(item) for item in line.split(',')]
            #remove list if there was actually just one item
            if len(line_value) == 1: line_value = line_value[0]
            option_value.append(line_value)
        #remove list if there was actually just one line
        if len(option_value) == 1: option_value = option_value[0]
        return option_value

    def _interpret(self, item_string):
        """Interpret a specific item string as one of several kinds of values
        Priority for conversions is: int > float > None > boolean > string

        Affected by:
        self._interpret_data -- do nothing if interpretation is disabled

        """
        if not self._interpret_data: return item_string #do nothing if disabled
        item_string = item_string.strip()
        try: return int(item_string) #int
        except ValueError: pass
        try: return float(item_string) #float
        except ValueError: pass
        if item_string == '': return None #None
        if item_string.lower() == 'false': return False
        if item_string.lower() == 'true': return True
        return item_string #do nothing if found no way to interpret



def main():
    pass

if __name__ == '__main__':
    main()


