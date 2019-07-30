# -*- coding: utf-8 -*-
# open source project
"""
Configuration classes.
"""
import io
import configparser
from collections import defaultdict, OrderedDict
from typing import Union

from tools.logger import logger
from tools.exceptions import UnknownError
from tools.helpers.interface import raise_anomaly
from tools.helpers.data_manager import open_file, save_file
from tools.helpers.models import Path, Singleton, Wildcard, BaseDict
from tools.helpers.config_manager.config_conversion import convert_dict_to_str
from tools.helpers.config_manager.config_dict import ConfigDict

DEFAULT_SECTION = "default"
ENCODING = "utf-8"
_ALLOWED_TYPES = (dict, OrderedDict, configparser.ConfigParser)


class _Config(BaseDict):
    """Class to easily create configurations.

    >>> def_conf_d = ConfigDict({DEFAULT_SECTION: {1: 5, 2: 6, 5: 7}, 2:{1: 8, 3: 9}, 'other':{1: 10, 4: 11}})
    >>> def_conf_d.default_section

    >>> def_conf_d.section

    >>> conf_d = ConfigDict({DEFAULT_SECTION: {1: 12, 2: 13, 6: 14}, 2:{1: 15}, 'other2':{1: 16, 4: 17}})
    >>> conf_d.default_section

    >>> conf_d.section

    >>> conf_d == def_conf_d
    False
    >>> config = _Config(default_config=def_conf_d, ask_path=False)
    >>> (config.section, config.default_section)
    ('default', 'default')
    >>> config.config
    ConfigDict:
    OrderedDict([('default', SectionDict:
    OrderedDict([('1', 5), ('2', 6), ('5', 7)])), ('2', SectionDict:
    OrderedDict([('1', 8), ('3', 9)])), ('other', SectionDict:
    OrderedDict([('1', 10), ('4', 11)]))])
    >>> config.config = conf_d
    >>> (config.section, config.default_section)
    ('default', 'default')
    >>> config.config
    ConfigDict:
    OrderedDict([('default', SectionDict:
    OrderedDict([('1', 12), ('2', 13), ('6', 14)])), ('2', SectionDict:
    OrderedDict([('1', 15)])), ('other2', SectionDict:
    OrderedDict([('1', 16), ('4', 17)]))])
    >>> config[1]
    12
    >>> config['2']
    13
    >>> config[5]
    7
    >>> config.load_config(2)
    >>> config.section
    '2'
    >>> config.load_config('other')
    >>> config.section
    'other'
    >>> config.config
    ConfigDict:
    OrderedDict([('default', SectionDict:
    OrderedDict([('1', 12), ('2', 13), ('6', 14), ('5', 7)])), ('2', SectionDict:
    OrderedDict([('1', 15)])), ('other2', SectionDict:
    OrderedDict([('1', 16), ('4', 17)])), ('other', SectionDict:
    OrderedDict([('1', 10), ('4', 11)]))])
    """
    _WILDCARD = Wildcard()
    EDITABLE_ATTR = ["path", "config", "default_config", "default_section", "section"]
    EDITABLE_PRIVATE_ATTR = ["auto_load", "force_load", "conversion_dict", "auto_cast", "write_flags", "ask_path",
                             "search_in_default_config", "auto_write"]

    def __init__(self, *args, **kwargs):
        """Initialisation of a _Config instance.

        :param args:  see 'init' method
        :param kwargs: see 'init' method
        """
        super().__init__()
        self._cfg = ConfigDict()  # current configuration
        self._default_config = ConfigDict()  # default configuration
        self._temp_config = OrderedDict()  # temporary configuration
        self._path = Path()  # current configuration path
        self._default_path = Path()  # default configuration path
        self._conversion_dict = None
        self._auto_cast = None
        self._write_flags = None
        self._force_load = None
        self._load_empty = None
        self._ask_path = None
        self._search_in_default_config = None
        self._init_count = 0
        self._policies = defaultdict(bool)  # by default every modification is forbidden  # WIP
        if args or kwargs:
            self.init(*args, **kwargs)
        logger.debug("Config object created.")

    def init(self, default_config: Union[dict, ConfigDict] = None, path: Union[str, Path] = None,
             auto_load: bool = True, default_section: str = DEFAULT_SECTION, section: str = None,
             conversion_dict: dict = None, force_load: bool = False, load_empty: bool = False,
             auto_cast: bool = False, write_flags: bool = None, ask_path: bool = True,
             search_in_default_config: bool = True, merge_default_how: str = 'right', **kwargs):
        """cf. __init__

        :param path: path of the current configuration file.
        :param default_config: default configuration dictionary-like object with two levels.
        Preferred type is ConfigDict.
        :param auto_load: if True, configuration file is loaded at initialisation.
        :param default_section: string of the default section in configuration file.
        :param section: current section of current configuration
        :param conversion_dict: conversion of string values into other types.
        :param force_load: argument for load method.
        :param load_empty: if True, empty configuration can overwrite existing one
        :param auto_cast: if True, the read configuration values are automatically converted to basic Python types
        :param write_flags: if None, same as auto_cast.
                            If True, flags are added to the written configuration keys to explicit value types
        :param ask_path: if True and path is None, the configuration path is asked to the user,
        otherwise, the path remains None. Actually, it is the argument of open_file function.
        :param search_in_default_config: if True, the default configuration is automatically used when a key
        is not found in the current configuration. If a section, which exists in default config
         and doesn't in current config, is tried to being accessed, it is created in the current config " todo
         :param merge_default_how: merge method for load method.
         Default is 'outer' (both existing and new keys are kept, values are updated)
         :param kwargs: other keyword arguments (not used)
        """
        # Check arguments
        if kwargs:
            logger.warning("Keyword arguments '{}' are not valid.".format(kwargs))
        # self._check_args(path=path, default_config=default_config, auto_load=auto_load,
        #                  default_section=default_section, section=section, conversion_dict=conversion_dict,
        #                  force_load=force_load, auto_cast=auto_cast, write_flags=write_flags)

        if not isinstance(conversion_dict, dict):
            conversion_dict = {}
        # Parameters
        self._auto_cast = auto_cast
        # if write_flags is not defined, write_flags is the same as auto_cast
        self._write_flags = auto_cast if write_flags is None else write_flags
        self._force_load = force_load
        self._load_empty = load_empty
        self._ask_path = ask_path
        self._search_in_default_config = search_in_default_config  # todo
        self._conversion_dict = conversion_dict
        # Load default config
        self._default_config = ConfigDict(default_config)
        self._cfg = self.default_config.deepcopy()  # first current configuration, before load  # todo: needed?
        # Sections
        if not isinstance(default_section, str):
            default_section = DEFAULT_SECTION
        self._default_config.default_section = default_section  # default section of default config
        self._default_config.section = self._default_config.default_section if section is None else section
        self.default_section = default_section  # default section of current config
        self.section = self.default_section if section is None else section
        # Paths
        self.path = path
        self._default_path = self._path.copy() or Path(path)  # if path is None, keep the first path
        # Load configuration from file
        if auto_load:
            self.load(merge_how=merge_default_how)
        self._init_count += 1
        logger.debug("Config initialized. Number of initialization(s): {}".format(self._init_count))

    def edit(self, **kwargs):
        """Edit attributes of the configuration."""
        for attr in self.EDITABLE_ATTR:
            kwarg = kwargs.pop(attr, self._WILDCARD)
            if kwarg is not self._WILDCARD:
                setattr(self, attr, kwarg)
                logger.debug("Attribute '{}' changed to '{}'.".format(attr, kwarg))

        for p_attr in self.EDITABLE_PRIVATE_ATTR:
            kwarg = kwargs.pop(p_attr, self._WILDCARD)
            if kwarg is not self._WILDCARD:
                setattr(self, "_" + p_attr, kwarg)
                logger.debug("Private attribute '{}' changed to '{}'.".format(p_attr, kwarg))
        logger.debug("Configuration edited.")

    def __setitem__(self, key, value):
        return self._cfg.__setitem__(key, value)

    def __repr__(self):
        return "{}:\nPath: {}\nDefault section: {}\nSection: {}\n\nData: {}\n" \
            .format(self.__class__.__name__, self.path, self.default_section, self.section, self._cfg)

    def __str__(self):
        string = "# path: {}\n{}".format(self.path, self._cfg)
        return string

    # Get values
    def __getitem__(self, item):
        if item in self._temp_config:  # 1st, try to find the key in temp config
            logger.debug("temporary config used for key '{}'".format(item))
            return self._temp_config[item]
        try:
            return self._cfg[item]  # 2nd, try to find the key in current config
        except KeyError as _err_msg:
            try:  # 3rd, try to find the key in default config TODO: use search in default config
                res = self._default_config[item]
                logger.debug("Item '{}' found in default configuration instead of current configuration.".format(item))
                self._cfg[item] = res  # set item to current configuration
                return res
            except KeyError as err_msg:
                raise KeyError(err_msg)

    def get(self, item, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def setdefault(self, k, default=None):
        return self._cfg.setdefault(k, default)

    def __call__(self, *args, **kwargs):
        """Access to a value with a specific section. Pattern: CONFIG(section, key, default)

        >>> config = _Config({DEFAULT_SECTION: {1: 12, 2: 17}, 2:{1: 15}, 'other2':{1: 16, 3: 18}}, ask_path=False)
        >>> config.default_section
        'default'
        >>> config(1)  # search key 1 in default section
        12
        >>> config('other2', 1)  # search key 1 in section 'other2'
        16
        >>> config(1, section=2)  # search key 1 in section 2
        15
        >>> config(3, default=8)  # search key 3 in default section, return 8 if not found
        8
        >>> config('other2', 2, default=9)  # search key 2 in section 'other2', then default section if not found
        17

        # search key 3 in section 2, then in default section if not found; return 10 if not found

        >>> config(3, section=2, default=10)
        10

        :param args: [key] or [section, key] o [section, key, default]
        :param kwargs: {} or {'section': section} or {'default': default_value}
        :return: self.get_section(section)[key]
        default_section is used if not passed as argument
        """
        if not args or (len(args) + len(kwargs) > 3):
            raise TypeError("Excepted 1 mandatory positional argument and keyword arguments 'section' and 'default'"
                            "or 1 to 2 other positional arguments".format(kwargs.keys()))
        section = args[0] if len(args) >= 2 else kwargs.pop('section', self.default_section)
        default = args[2] if len(args) == 3 else kwargs.pop('default', self._WILDCARD)
        if kwargs:  # if other kwargs
            raise TypeError("Keyword arguments '{}' are not supported".format(kwargs.keys()))
        key = args[1] if len(args) >= 2 else args[0]
        # search in the section of the current configuration
        if key in self.get_section(section):
            return self.get_section(section)[key]
        # search in the default section of the current configuration
        elif key in self.get_section(self.default_section):
            return self.get_section(self.default_section)[key]
        # search in the section of the default configuration
        elif key in self._default_config.get_section(section) and self._search_in_default_config:
            return self._default_config.get_section(section)[key]
        # search in the default section of the default configuration
        elif key in self._default_config.get_section(self.default_section) and self._search_in_default_config:
            return self._default_config.get_section(self._default_config.default_section)[key]
        elif default is not self._WILDCARD:
            return default
        else:
            err_msg = "'{}' is not a valid key for the configuration".format(key)
            logger.error(err_msg)
            raise KeyError(err_msg)
            # return self._WILDCARD

    @property
    def temp_config(self):
        return self._temp_config

    @temp_config.setter
    def temp_config(self, other):
        self._temp_config = OrderedDict(other)
        logger.debug("Temporary configuration set to: {}".format(self._temp_config))

    # Sections
    def _check_section(self, section: Union[str, list], search_in_default_config: bool = None):
        """If the section doesn't exist and search_in_default_config,
        append the section from default config to current configuration"""
        section = None if section is None else ConfigDict.TO_KEY_FUNC(section)
        search_in_default_config = self._search_in_default_config if search_in_default_config is None \
            else search_in_default_config
        if section not in self.sections() and section is not None and search_in_default_config:
            # if the section doesn't exist, append the default configuration to the configuration
            self.add_default_config_sections(sections=section)
            # self.reload_default(write=False, how='append')  # old method
            logger.debug("Section(s) '{}' of default configuration appended to config.".format(section))
        return section

    def get_section(self, section=None, set_section=False, add_section=False, search_in_default_config=None):
        """Returns the SectionDict associated to the 'section' key

        :param section: ConfigDict key
        :param set_section: if True, set the section to current configuration
        :param add_section: if True and the section doesn't exist, create it
        :param search_in_default_config: if True and the section doesn't exist, use default config section if it exists
        :return:
        """
        section = self._check_section(section, search_in_default_config=search_in_default_config)
        return self._cfg.get_section(section=section, set_section=set_section, add_section=add_section)

    def set_section(self, section=None, add_section=True, search_in_default_config=None):
        section = self._check_section(section, search_in_default_config=search_in_default_config)
        self._cfg.set_section(section=section, add_section=add_section)

    def load_config(self, section=None):
        """alias of set_section, with search_in_default_config argument True by default."""
        self.set_section(section, search_in_default_config=True)

    def add_section(self, section, section_dict=None, auto_cast=False, exist_ok=False):
        self._cfg.add_section(section, section_dict, auto_cast=auto_cast, exist_ok=exist_ok)

    def _check_args(self, path=None, default_config=None, auto_load=True,
                    default_section=DEFAULT_SECTION, section=None, conversion_dict=None,
                    force_load=False, auto_cast=False, write_flags=None):
        # TODO
        pass

    # Updates/merges
    def merge(self, config_dict, how='outer', how_section=None, inplace=False):
        if isinstance(config_dict, _Config):
            config_dict = config_dict.config
        return self._cfg.merge(config_dict, how=how, how_section=how_section, inplace=inplace)

    def append(self, other):
        return self.merge(other, how='outer', how_section='append', inplace=True)

    def update(self, other):
        return self.merge(other, how='outer', how_section='outer', inplace=True)

    def replace(self, other):
        return self.merge(other, how='right', how_section='right', inplace=True)

    def clear(self, section=None):
        return self._cfg.clear(section=section)

    # Getters & setters of main attributes
    @property
    def init_count(self):
        return self._init_count

    @init_count.setter
    def init_count(self, _value):
        logger.error("AttributeError: 'init_count' attr can not be changed this way!")

    @property
    def default_path(self):
        return self._default_path

    @default_path.setter
    def default_path(self, _value):
        logger.error("AttributeError: 'default_path' attr can not be changed this way!")

    @property
    def path(self):
        return self._path

    @path.setter
    def path(self, path):
        if self._path.isnone:
            title = "Select a configuration file to load."
        else:
            title = "Bad configuration file set. Please select a valid configuration file."
        title += " [Cancel for default configuration]"
        self._path = open_file(path, title=title, ask_path=self._ask_path, behavior_on_cancellation='ignore')
        logger.debug("Config path set to '{}'".format(self._path))

    def get_output_path(self):
        return self.default_path if self._path.isnone else self.path

    @property
    def default_section(self):
        return self._cfg.default_section

    @default_section.setter
    def default_section(self, name):
        self._cfg.default_section = name
        # self._default_config.default_section = name

    @property
    def section(self):
        return self._cfg.section

    @section.setter
    def section(self, name):
        self._cfg.section = name

    def sections(self):  # function, not property, like Configparser.
        return [section for section in self]

    @property
    def default_config(self):  # TODO : copy ?
        return self._default_config  # .deepcopy()

    @property
    def config(self):  # TODO : copy ?
        return self._cfg

    @config.setter
    def config(self, config_dict):
        """alias to _cfg attribute

        >>> def_conf_d = ConfigDict({DEFAULT_SECTION: {1: 5, 2: 6, 5: 7}, 2:{1: 8, 3: 9}, 'other':{1: 10, 4: 11}})
        >>> conf_d = ConfigDict({DEFAULT_SECTION: {1: 12, 2: 13, 6: 14}, 2:{1: 15}, 'other2':{1: 16, 4: 17}})
        >>> config = _Config(default_config=def_conf_d)
        >>> config.config
        15

        >>> config.config = conf_d
        >>> config.config
        0

        :param config_dict:
        :return:
        """
        self._cfg.config = config_dict

    @property
    def config_dict(self):
        return self.config

    def load(self, path=None, force_load=None, auto_cast=None, load_empty=None, merge_how='right'):
        """Load configuration from file.
        If force-load, reload_default values on error.."""
        path = self._path if path is None else Path(path)
        auto_cast = self._auto_cast if auto_cast is None else auto_cast
        force_load = self._force_load if force_load is None else force_load
        load_empty = self._load_empty if load_empty is None else load_empty
        if not path.isfile:
            if force_load:
                self.reload_default()
            return None
        config_dict = self.read_config(path, auto_cast=auto_cast)
        if config_dict is None:
            if force_load:
                self.reload_default()
            return None
        elif path.isfile:  # Change path
            self._path = path
            logger.debug("Path changed to '{}' with 'load' method.".format(self.path))
        elif config_dict.isempty:
            if not load_empty:
                logger.info("Configuration loaded is empty! It won't replace the existing one.")
                logger.debug("Use 'clear' method to empty the ConfigDict")
                return None
        else:
            raise UnknownError("bad case in 'load'")
        # config_dict.section = self.section
        # config_dict.default_section = self.default_section
        # config_dict._conversion_dict = self._conversion_dict
        self.merge(config_dict, how=merge_how, inplace=True)
        logger.info("Configuration loaded!")

    def add_default_config_sections(self, sections=None, add_empty_sections=False):
        dico = self.default_config.deepcopy()
        sections = {sections} if isinstance(sections, str) else sections
        n_dico = {k: dico[k] for k in sections & dico} if sections is None else dico
        if add_empty_sections:
            for section in sections:
                self.add_section(section, exist_ok=True)
        self.merge(n_dico, how='append', inplace=True)

    def reload_default(self, write=True, backup=True, how='right', how_section=None, sections=None):
        """Set path and config to default values.
        If write is True, overwrite default file with default configuration."""
        # self._cfg = self.default_config.deepcopy()
        self._path = self._default_path.copy()
        dico = self.default_config.deepcopy()
        sections = {sections} if isinstance(sections, str) else sections
        n_dico = dico if sections is None else {k: dico[k] for k in sections & dico.keys()}
        self.merge(n_dico, how=how, how_section=how_section, inplace=True)
        if write:
            self.save_config(overwrite=True, backup=backup)
            logger.info("Configuration reloaded and saved to '{}'.".format(self._path))
        else:
            logger.info("Configuration reloaded.")

    # Read methods

    # def read(self, *args, **kwargs):  # deprecated
    #     if args and isinstance(args[0], io.TextIOBase):  # Support of Configparser behavior
    #         logger.warning("Bad practice: do not pass a file through 'write' method, prefer a path!")
    #         args[0].close()
    #         args = (args[0].name, *args[1:])
    #     return self.read_config(*args, **kwargs)

    @classmethod
    def read_config(cls, path, auto_cast=True, anomaly_flag='warning'):
        """Returns a config_dict read from a INI file."""
        # WARNING: No check of input arguments !
        # Read the configuration file with configparser
        config_parser = configparser.ConfigParser()
        try:
            config_parser.read(path, encoding=ENCODING)
        except (configparser.Error, ValueError, KeyError, TypeError) as err:
            logger.exception(err)
            msg = "The configuration could not be loaded!\n" \
                  "Please check that the configuration file is correct.\n" \
                  "Original error: {}".format(err)
            raise_anomaly(flag=anomaly_flag, error=err.__class__,
                          title="Configuration loading failed!", message=msg)
            return None
        return ConfigDict(config_parser, auto_cast=auto_cast)

    # Write methods
    def save_config(self, path=None, overwrite=True, backup=False, auto_mkdir=True,
                    write_flags=None, anomaly_flag='warning', ask_path=False, default_config=False):
        write_flags = self._write_flags if write_flags is None else write_flags
        path = self.get_output_path() if path is None else path
        path = save_file(path, ask_path=ask_path, overwrite=overwrite,
                         backup=backup, auto_mkdir=auto_mkdir)
        if path.isnone:
            logger.error("No valid path set. Configuration has not been saved.")
            return
        config_dict = self.default_config if default_config else self.config
        path = self.write_config(path, config_dict, write_flags=write_flags, anomaly_flag=anomaly_flag)
        if path is not None:
            self._path = path

    # def write_config(cls, *args, **kwargs):  # NXVER
    #     return ConfigDict.write_config(*args, **kwargs)

    # def write(self, *args, **kwargs):  # deprecated
    #     if args and isinstance(args[0], io.TextIOBase):  # Support of Configparser behavior
    #         logger.warning("Bad practice: do not pass a file through 'write' method, prefer a path!")
    #         args[0].close()
    #         args = (args[0].name, *args[1:])
    #     return self.write_config(*args, **kwargs)

    @staticmethod
    def _write_configparser(config_dict, write_flags=False):
        config_parser = configparser.ConfigParser()
        for section in config_dict:
            config_parser.add_section(section)
            section_dict = convert_dict_to_str(config_dict.get(section)) \
                if write_flags else config_dict.get(section)
            for key, value in section_dict.items():
                config_parser.set(section, str(key), str(value))
        return config_parser

    @classmethod
    def write_config_bug(cls, path, config_dict, backup=True, overwrite=True,
                         auto_mkdir=True, write_flags=False, anomaly_flag='warning'):  # todo buggy method
        # WARNING: No check of input arguments !
        # Get path
        path = save_file(path, overwrite=overwrite, backup=backup, auto_mkdir=auto_mkdir)
        # Load Configparser object
        config_parser = cls._write_configparser(config_dict, write_flags=write_flags)
        # Write Configparser object to disk
        try:
            with open(path, mode='w', encoding=ENCODING, newline=None) as file:
                config_parser.write(file)
        except (configparser.Error, PermissionError, FileNotFoundError) as err:
            logger.exception(err)
            msg = "Configuration could not be written to disk!\n" \
                  "Original error: {}".format(err)
            raise_anomaly(flag=anomaly_flag, error=err.__class__,
                          title="Configuration writing failed!", message=msg)
            return None
        logger.info("Configuration successfully written to disk: {}".format(path))
        # logger.debug("Configuration written: {}".format(config_dict))
        return path

    @classmethod
    def write_config(cls, path, config_dict, write_flags=False, anomaly_flag='warning'):
        # WARNING: No check of input arguments !
        # config_dict = convert_dict_to_str(config_dict) if write_flags else config_dict  # WRONG: ConfigDict not convertible!
        # Write Configparser object to disk
        try:
            with open(path, mode='w', encoding=ENCODING, newline=None) as file:
                file.write(config_dict.to_str(write_flags=write_flags))
        except (configparser.Error, PermissionError, FileNotFoundError) as err:
            logger.exception(err)
            msg = "Configuration could not be written to disk!\n" \
                  "Original error: {}".format(err)
            raise_anomaly(flag=anomaly_flag, error=err.__class__,
                          title="Configuration writing failed!", message=msg)
            return None
        logger.info("Configuration successfully written to disk: {}".format(path))
        # logger.debug("Configuration written: {}".format(config_dict))
        return path


class Config(_Config, metaclass=Singleton):
    """Unique configuration (singleton)"""

    def __init__(self, *args, **kwargs):
        if args or kwargs:
            logger.warning("Config object doesn't take any argument.")
        super().__init__()


if __name__ == "__main__":
    _CONFIG = Config()
    _CONFIG.path = 'tools/config/config.ini'
    _CONFIG.load()
    import pdb

    pdb.set_trace()
