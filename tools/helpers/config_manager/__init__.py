# -*- coding: utf-8 -*-
# open source project
"""
Configuration loaded from/saved to disk with INI syntax.

As the configuration is a singleton (the configuration class can only have a unique instance),
it can be accessed by calling Config class directly. For example:

>>> CONFIG = Config()
>>> CONFIG2 = Config()
>>> CONFIG is CONFIG2
True

Configuration is 2-levels dictionary-like object, but its values can be accessed like a 1-level dictionary.
                Config
    _____________|  |______________________________________________________________________________________________
    |                     |                              |                      |                    |            |
 config (ConfigDict)  default_config (ConfigDict)  temp_config (OrderedDict)  path (Path)  default_path (Path)  other
   |__________________________________________________________________
      |                        |                                     |
   config (OrderedDict)  default_section (default key of config)   section (current key of config)
      |
  SectionDict
      |
   config (OrderedDict)


# Methods to get elements

## Get item: CONFIG[item]
    1) Search in the current section 'section' of the current config 'config' (loaded from disk)
       Equivalent 2-levels dictionary: CONFIG[section][item]
       On KeyError, continue to search:
    2) Search in the default section 'default_section' of the current config 'config'
       Equivalent 2-levels dictionary: CONFIG[default_section][item]
       On KeyError, continue to search:
    3) Search in the current section 'section' of the default config 'default_config' (hard coded)
       Equivalent 2-levels dictionary: CONFIG.default_config[section][item]
       On KeyError, continue to search:
    4) Search in the default section 'default_section' of the default config 'default_config'
       Equivalent 2-levels dictionary: CONFIG.default_config[default_section][item]
       On KeyError, raise KeyError

## Call: CONFIG(item) or CONFIG(section, item) or CONFIG(section, item, default)
Possible cases:
    a. item is the only argument: CONFIG(item)
    b. item and default are the only arguments: CONFIG(item, default=default)
        1) search in default section of current configuration,
        2) search in default section of default configuration,
        3) a) raise KeyError
        3) b) return default
    c. section is referenced: CONFIG(section, item) or CONFIG(item, section=section)
    d. section and default are referenced: CONFIG(section, item, default)
       or CONFIG(section, item, default=default)  or CONFIG(item, section=section, default=default)
        1) search in current section of current configuration,
        2) search in default section of current configuration,
        3) search in current section of default configuration,
        4) search in default section of default configuration,
        5) c) raise KeyError
        5) d) return default

# Initialization
TODO

# Load/Save configuration
TODO

"""
from tools.helpers.config_manager.config_models import Config

__all__ = ['Config',
           ]

__version__ = '0.7.0'
