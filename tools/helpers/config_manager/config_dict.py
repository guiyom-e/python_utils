# open source
import configparser
from collections import defaultdict, OrderedDict
from copy import copy, deepcopy
import datetime
from typing import Union

from tools.logger import logger
from tools.helpers.models import Path, Reference, Wildcard
from tools.helpers.utils import merge_dict_preprocessing
from tools.helpers.config_manager.config_conversion import convert_dict_from_str, convert_dict_to_str

_DEFAULT_DICT = OrderedDict


def to_key(*args):
    """Converts the last argument into a valid key of SectionDict."""
    if not args:
        raise TypeError("{} takes at least 1 argument (0 given)".format(to_key.__name__))
    obj = args[-1]
    try:
        n_str = str(obj).lower().strip()  # case insensitive
    except TypeError as te:
        logger.exception(te)
        return None
    return n_str


def to_section(*args):
    """Converts the last argument into a valid section of ConfigDict."""
    if not args:
        raise TypeError("{} takes at least 1 argument (0 given)".format(to_section.__name__))
    obj = args[-1]
    try:
        n_str = str(obj).strip()  # case sensitive
    except TypeError as te:
        logger.exception(te)
        return None
    return n_str


class BaseDict:
    """Abstract class of dictionary-like objects, parent of SectionDict and ConfigDict."""
    TO_KEY_FUNC = lambda _, x: x
    _DEFAULT_DICT = _DEFAULT_DICT

    def __init__(self, *args, **kwargs):
        self._cfg = self._DEFAULT_DICT(*args, **kwargs)

    def __repr__(self):
        return "{}:\n{}".format(self.__class__.__name__, self._cfg)

    def __iter__(self):
        for key in self._cfg:
            yield key

    def __len__(self):
        return len(self._cfg)

    def __getitem__(self, item):
        n_item = self.TO_KEY_FUNC(item)
        return self._cfg[n_item]

    def __setitem__(self, key, value):
        self._cfg[key] = value

    def __eq__(self, other):
        return self._cfg == other

    # Inherited from dict
    @staticmethod
    def fromkeys(*args, **kwargs):
        n_dict = _DEFAULT_DICT.fromkeys(*args, **kwargs)
        return __class__(n_dict)

    def get(self, item, default=None):
        item = self.TO_KEY_FUNC(item)
        return self._cfg.get(item, default)

    def copy(self):
        return copy(self)

    def deepcopy(self):
        return deepcopy(self)

    def setdefault(self, k, default=None):
        k = self.TO_KEY_FUNC(k)
        self._cfg.setdefault(k, default)
        return self[k]

    def clear(self):
        self._cfg.clear()

    def keys(self):
        return self._cfg.keys()

    def values(self):
        return self._cfg.values()

    def items(self):
        return self._cfg.items()

    def update(self, other):
        self.update(other)
        return None

    def pop(self, item, default=None):
        return self._cfg.pop(item, default)

    def popitem(self, item):
        return self._cfg.popitem(item)

    # Inherited from OrderedDict
    def move_to_end(self, key):
        key = self.TO_KEY_FUNC(key)
        return self._cfg.move_to_end(key)

    # Inherited from pandas dataframe
    @classmethod
    def from_dict(cls, dico):
        return cls(dico)


class SectionDict(BaseDict):
    """Dictionary-like class."""

    # Class attributes
    _ALLOWED_TYPES = (str, int, float, list, tuple, Path, Reference, datetime.datetime)
    _BASE_POLICY = defaultdict(bool, {'setprivattr': True,  # mandatory
                                      'chprivattr': True,  # mandatory
                                      'setitem': True,
                                      'clear': True,
                                      'forbid_none_value': False,
                                      })
    _POLICIES = '__policies__'
    _CONFIG = '_cfg'
    TO_KEY_FUNC = to_key
    _DEFAULT_DICT = _DEFAULT_DICT
    _WILDCARD = Wildcard()
    assert isinstance(_DEFAULT_DICT(), dict)

    ###################
    # Builtin methods #
    ###################

    def __init__(self, dico=None, auto_cast=False):  # Overridden method of BaseDict
        self.__policies__ = self._BASE_POLICY.copy()
        super().__init__()
        self._cfg = self._DEFAULT_DICT()
        self._build(dico, auto_cast=auto_cast)
        self.__policies__['setprivattr'] = False
        self.__policies__['chprivattr'] = False

    @classmethod
    def _check_allowed_value_type(cls, value):
        if value is None:
            if cls._BASE_POLICY['forbid_none_value']:
                return False
            else:
                # todo
                logger.warning("Setting a None value in a SectionDict is a bad practice (can cause unexpected errors).")
                return True
        if isinstance(value, cls._ALLOWED_TYPES):
            return True
        return False

    @classmethod
    def _new(cls, dico, auto_cast=False, deepcopy_values=True, copy_values=True, **conversion_kwargs):
        """Returns a dictionary-like object which can be set as '_cfg' attribute.

        :param conversion_kwargs: keywords arguments for convert_dict_from_str,
        except 'inplace' which is automatically True.
        """
        if isinstance(dico, list):
            try:
                dico = cls._DEFAULT_DICT(dico)
            except TypeError:
                dico = []
        if dico is None:
            o_dict = cls._DEFAULT_DICT()
            return o_dict
        elif isinstance(dico, SectionDict):
            o_dict = cls._new(dico._cfg, auto_cast=auto_cast, deepcopy_values=deepcopy_values, copy_values=copy_values)
            return o_dict
        elif isinstance(dico, configparser.SectionProxy):
            o_dict = SectionDict(cls._DEFAULT_DICT([(cls.TO_KEY_FUNC(k), v) for k, v in dico.items()]),
                                 auto_cast=auto_cast)
            return o_dict
        elif isinstance(dico, dict):
            o_dict = cls._DEFAULT_DICT()
            for k, v in dico.items():
                n_k = cls.TO_KEY_FUNC(k)
                if not cls._check_allowed_value_type(v) or not n_k:
                    logger.error("Input items '({}, {})' not taken in charge.".format(k, v))
                    continue
                if n_k in o_dict:  # TODO renaming policy ?
                    logger.warning("keys with different case not allowed. "
                                   "key '{}' dropped. renaming not implemented.".format(k))
                    continue
                if deepcopy_values:
                    v = deepcopy(v)
                elif copy_values:
                    v = copy(v)
                o_dict[n_k] = v
        else:
            logger.error("Bad type '{}' for object '{}'. Expected dict or SectionDict objects".format(type(dico), dico))
            return None
        if auto_cast:
            if 'no_flag' not in conversion_kwargs:
                conversion_kwargs['no_flag'] = 'auto-conversion'
            conversion_kwargs['inplace'] = True
            convert_dict_from_str(o_dict, **conversion_kwargs)
        return o_dict

    def _build(self, dico, update=False, auto_cast=False, deepcopy_values=True, copy_values=True):
        """Build SectionDict data

        >>> sd = SectionDict({"a": 1, 3: 4})
        >>> sd._build({"a": 2, "b": 6}, update=False)
        >>> sd
        SectionDict:
        OrderedDict([('a', 2), ('b', 6)])
        >>> sd._build({"b": 5, "c": 7}, update=True)
        >>> sd
        SectionDict:
        OrderedDict([('a', 2), ('b', 5), ('c', 7)])

        :param dico: dictionary-like object
        :param update: if False, clear the current self._cfg dictionary before updating it
        :param auto_cast: if True, auto cast values to the correct Python type
        :param deepcopy_values: if True, deepcopy values
        :param copy_values: if True, copy values
        :return: None
        """
        o_dict = self._new(dico, auto_cast=auto_cast, deepcopy_values=deepcopy_values, copy_values=copy_values)
        if not update:
            self._cfg.clear()
        self._cfg.update(o_dict)

    def __getitem__(self, item):  # Overridden methods of BaseDict
        """Get item

        >>> sd = SectionDict({"a": 1, 3: 4})
        >>> sd["a"]
        1
        >>> sd[3] == sd[sd.TO_KEY_FUNC(3)]
        True
        """
        n_item = self.TO_KEY_FUNC(item)
        if n_item is not None:
            return self._cfg[n_item]  # TODO: policy on error?
        return None

    def __setitem__(self, key, value):  # Overridden method of BaseDict # TODO policy !
        """ Set item

        >>> sd = SectionDict({"a": 1, 3: 4})
        >>> sd.__policies__['setitem'] = True
        >>> sd["a"] = 2
        >>> sd["a"]
        2
        >>> sd[9] = 5
        >>> sd[9]
        5
        """
        if self.__policies__['setitem']:
            self._build({key: value}, update=True)

    def __getattr__(self, item):
        """ Get item using getattr method

        >>> sd = SectionDict({"a": 1, 3: 4})
        >>> sd.a == sd["a"]
        True
        >>> sd.a
        1
        """
        if item.startswith("_"):
            return super().__getattribute__(item)
        try:
            return self[item]
        except KeyError as ke:
            raise AttributeError(ke)

    def __setattr__(self, key, value):  # Overridden methods of BaseDict
        if key.startswith("_"):
            _key_bool = key in dir(self)
            if (not _key_bool and (key == self._POLICIES or self.__policies__['setprivattr'])) \
                    or (_key_bool and self.__policies__['chprivattr']):
                return super().__setattr__(key, value)
            else:
                logger.error("Forbidden! The policy does not allow to set the private attribute '{}'.".format(key))
                return
        return self.__setitem__(key, value)

    def __delitem__(self, key):
        key = self.TO_KEY_FUNC(key)
        if self.__policies__['delitem']:
            del self._cfg[key]
            return self
        else:
            logger.error("Forbidden! The policy does not allow to delete the key '{}'.".format(key))
            return

    def __delattr__(self, name):  # Overridden method of object
        if name.startswith("_"):
            if self.__policies__['delprivattr']:
                return super(self.__class__, self).__delattr__(name)
            else:
                logger.error("Forbidden! The policy does not allow to delete the private attribute '{}'.".format(name))
                return
        return self.__delitem__(name)

    def __eq__(self, other):
        if not isinstance(other, SectionDict):
            other = self.__class__(other)
        return self._cfg == other._cfg

    ##################
    # Public methods #
    ##################

    # Overridden methods of BaseDict
    def setdefault(self, k, default=None):
        if self.__policies__['setitem']:
            k = self.TO_KEY_FUNC(k)
            self.merge({k: default}, how='append', inplace=True)  # TODO policies / copy ?
            return self[k]
        else:
            logger.error("Forbidden! The policy does not allow to set items in the SectionDict.")

    def clear(self):
        if self.__policies__['clear']:
            self._build(None, update=False)
        else:
            logger.error("Forbidden! The policy does not allow to clear the SectionDict.")

    def update(self, other):
        self.merge(other, how='outer', inplace=True)
        return None

    # Added methods
    def merge(self, section_dict, how='outer', inplace=False):
        if not isinstance(section_dict, (dict, SectionDict)):
            logger.error("bad type for dict_to_merge")
            return self
        if inplace:
            left_dict = self
        else:
            left_dict = self.deepcopy()
        right_dict = section_dict
        m_dict = self._merge_dict(left_dict, right_dict, how=how)
        return None if inplace else m_dict

    @staticmethod
    def _merge_dict(left_dict, right_dict, how='outer'):
        if not isinstance(left_dict, __class__):
            left_dict = __class__(left_dict)
        keys, update = merge_dict_preprocessing(left_dict, right_dict, how=how)
        left_dict._build({k: right_dict[k] for k in keys}, update=update)
        # logger.debug("Merge '{}' ok.".format(how))
        return left_dict

    def to_str(self, write_flags=False):
        string = ""
        sec_dict = convert_dict_to_str(self) if write_flags else self
        for k, v in sec_dict.items():
            string += "{} = {}\n".format(k, v)
        return string


########################################################################################################################
########################################################################################################################
########################################################################################################################


class ConfigDict(BaseDict):
    """ConfigDict class

    >>> def_conf_d = ConfigDict({'a': {1: 5, 2: 6, 5: 7}, 2: {1: 8, 3: 9}, 'other': {1: 10, 4: 11}})
    >>> conf_d = ConfigDict({'a': {1: 12, 2: 13, 6: 14}, 2: {1: 15}, 'other2': {1: 16, 4: 17}})
    >>> conf_d.config
    OrderedDict([('a', SectionDict:
    OrderedDict([('1', 12), ('2', 13), ('6', 14)])), ('2', SectionDict:
    OrderedDict([('1', 15)])), ('other2', SectionDict:
    OrderedDict([('1', 16), ('4', 17)]))])
    >>> conf_d.config = conf_d
    >>> conf_d.config
    OrderedDict([('a', SectionDict:
    OrderedDict([('1', 12), ('2', 13), ('6', 14)])), ('2', SectionDict:
    OrderedDict([('1', 15)])), ('other2', SectionDict:
    OrderedDict([('1', 16), ('4', 17)]))])
    >>> conf_d.config = def_conf_d
    >>> conf_d.config
    OrderedDict([('a', SectionDict:
    OrderedDict([('1', 5), ('2', 6), ('5', 7)])), ('2', SectionDict:
    OrderedDict([('1', 8), ('3', 9)])), ('other', SectionDict:
    OrderedDict([('1', 10), ('4', 11)]))])
    """
    TO_KEY_FUNC = to_section
    _DEFAULT_DICT = _DEFAULT_DICT
    _ALLOWED_TYPES = (dict, OrderedDict, configparser.ConfigParser)
    _WILDCARD = object()

    def __init__(self, dico=None, auto_cast=False, default_section=_WILDCARD, section=_WILDCARD):
        super().__init__()
        self._cfg = self._DEFAULT_DICT()
        self._default_section = None  # todo: manage case of _cfg without default_section key
        self._section = None
        self._conversion_dict = None
        if dico is not None:
            self._build(dico, auto_cast=auto_cast, default_section=default_section, section=section)

    def _build(self, dico, auto_cast=False, default_section=_WILDCARD, section=_WILDCARD):
        f_dico = self._format_config_dict(dico, auto_cast=auto_cast)
        if f_dico is None:
            logger.debug("ConfigDict has not been built because 'None' value can not be formatted to ConfigDict.")
        else:
            self._cfg = f_dico
            logger.debug("ConfigDict object built with config: {}".format(self._cfg))
        self.section = section  # changes section except if it is _WILDCARD
        self.default_section = default_section  # changes default_section except if it is _WILDCARD

    @classmethod
    def _format_config_dict(cls, dico, auto_cast=False) -> Union[_DEFAULT_DICT, None]:
        if dico is None:
            return None
        if isinstance(dico, (list, zip, map)):  # todo: simpler way
            try:
                dico = OrderedDict(dico)
            except TypeError:
                logger.error("Bad format for '{}' object".format(dico))
                return None
        _new_allowed_types = (*cls._ALLOWED_TYPES, ConfigDict)
        if not isinstance(dico, _new_allowed_types):
            logger.error("Bad type '{}' for object '{}'. Expected '{}' object."
                         .format(type(dico), dico, " or ".join([str(t) for t in _new_allowed_types])))
            return None
        dico = OrderedDict([(cls.TO_KEY_FUNC(key), SectionDict(section, auto_cast=auto_cast))
                            for key, section in dico.items()])
        return dico

    # Conversion dict
    # for key, type_v in conversion_dict.items():  # TODO
    #     key = key.lower().strip()
    #     if not hasattr(type_v, '__call__'):
    #         logger.error("Values of conversion dict must be callable, not '{}'".format(type_v))
    #         continue
    #     try:
    #         config_dict[key] = type_v(config_dict[key])
    #     except ValueError:
    #         logger.warning("Wrong type for key {} and value {}"
    #                        .format(key, config_dict.get(key, None)))
    #     except KeyError:
    #         logger.warning("Key {} is not in config_dict dict"
    #                        .format(key))
    #     except Exception as exe:
    #         logger.exception(exe)
    #         logger.error("Could not convert the config_dict")
    # return config_dict

    def __getitem__(self, item):
        key = to_key(item)
        # section = self.TO_KEY_FUNC(item)
        if self.section and key in self._cfg[self.section]:  # First, search in current section
            return self._cfg[self.section][key]
        elif self.default_section and key in self._cfg[self.default_section]:  # Then, search in default section
            return self._cfg[self.default_section][key]
        # elif section in self:  # Then, search in sections (bad practice)
        #     logger.warning("Bad practice to access section '{}' by getitem. "
        #                    "Do prefer 'get_section' method.".format(section))
        #     return self.get_section(section=item, set_section=False)
        else:  # Finally raises an error if nothing found
            err_msg = "'{}' is not a valid key for the current configuration".format(item)
            logger.debug(err_msg)
            raise KeyError(err_msg)

    def get(self, item: str, default=None):
        try:
            return self[item]
        except KeyError:
            return default

    def __setitem__(self, key, value):
        key = self.TO_KEY_FUNC(key)
        # If key already exists in section, update section
        if self.section and key in self._cfg[self.section]:
            self._cfg[self.section][key] = value
        # If key already exists in default section, update default section
        elif self.default_section and key in self._cfg[self.default_section]:
            self._cfg[self.default_section][key] = value
        # If section is not None, i.e. exists, set value in section
        elif self.section:
            self._cfg[self.section][key] = value
        # If default section is not None, i.e. exists, set value in default section
        elif self.default_section:
            logger.debug("Item '({}, {})' set in default_section '{}' "
                         "because no section is set.".format(key, value, self.default_section))
            self._cfg[self.default_section][key] = value
        # If no section nor default section, error
        else:
            logger.error("No section nor default_section is defined! Setting item is not possible!\n"
                         "NB: to create a section, use 'add_section' method.")

    def __eq__(self, other) -> bool:
        """
        >>> ConfigDict({1: {8: 2}}) == ConfigDict({1: {8:2}})
        True
        >>> ConfigDict({1: {8: 3}}) == ConfigDict({1: {8:2}})
        False
        >>> ConfigDict({1: {8: 2}}) == {1: {8:2}}
        True
        >>> ConfigDict({1: {8: 2}}) == ConfigDict({1: SectionDict({8:2})})
        True
        """
        if not isinstance(other, ConfigDict):
            other = ConfigDict(other)
        return self._cfg == other._cfg

    def to_str(self, write_flags=False) -> str:
        string = "# ConfigDict object representation\n"
        for section in self:
            string += "[{}]\n".format(section)
            sec_dict = self.get_section(section, set_section=False)
            string += sec_dict.to_str(write_flags=write_flags)
            string += '\n'
        return string

    def __str__(self):
        return self.to_str()

    def clear(self, section=None):
        if section in self:
            self.get_section(section, set_section=False).clear()
        elif section is None:
            self._cfg.clear()
        else:
            logger.warning("Bad section '{}'. Configuration has not been cleared.".format(section))

    # Sections
    def get_section(self, section=None, set_section=False, add_section=False) -> Union[SectionDict, None]:
        """Get the ConfigDict section (SectionDict). If section is None, the default section is used.

        :param section: section string
        :param set_section: if True, set section
        :param add_section: if True and section doesn't exist, create it
        :return: SectionDict associated to section
        """
        section = None if section is None else self.TO_KEY_FUNC(section)
        if section is None:
            section = self.default_section
        if section not in self:
            logger.error("Bad section to get: '{}'!".format(section))
            return
        if set_section:
            self.set_section(section, add_section=add_section)
        return self._cfg[section]

    def set_section(self, section=None, add_section=True) -> None:
        section = None if section is None else self.TO_KEY_FUNC(section)
        if section is not None and section not in self and add_section:
            self.add_section(section)
        if section in self or section is None:
            self._section = section
        else:
            logger.error("Bad section to set: '{}'!".format(section))

    def add_section(self, section, section_dict=None, auto_cast=False,
                    exist_ok=False, set_section=False) -> None:
        section = None if section is None else self.TO_KEY_FUNC(section)
        if section in self:
            if not exist_ok:
                logger.error("Section '{}' already exists!".format(section))
        else:
            self._cfg[section] = SectionDict(section_dict, auto_cast=auto_cast)
        logger.debug("Section '{}' added.".format(section))
        if set_section:
            self._section = section

    @property
    def default_section(self) -> str:
        return self._default_section

    @default_section.setter
    def default_section(self, name):
        if name is self._WILDCARD:  # _WILDCARD is used to ignore the setter
            return
        name = None if name is None else self.TO_KEY_FUNC(name)
        if name not in self and name is not None:
            logger.debug("Default section name '{}' doesn't exist and will be created.".format(name))
            self.add_section(name)
        self._default_section = name

    @property
    def section(self) -> str:
        return self._section

    @section.setter
    def section(self, name):
        if name is self._WILDCARD:  # _WILDCARD is used to ignore the setter
            return
        name = None if name is None else self.TO_KEY_FUNC(name)
        if name not in self and name is not None:
            logger.error("Bad section name '{}'. To create a section, use 'add_section' method".format(name))
            return
        self._section = name

    def sections(self) -> list:  # function, not property, like Configparser.
        return [section for section in self]

    @property
    def config(self) -> Union[_DEFAULT_DICT, None]:
        return self._cfg

    @config.setter
    def config(self, config_dict: Union[dict, None, 'ConfigDict']):
        """
        :param config_dict: dictionary-like object
        :return: None
        """
        self.merge(config_dict, how='right', inplace=True)

    @property
    def isempty(self) -> bool:
        ls_empty = [ele for ele in self.values()]
        return not (True in ls_empty)

    @property
    def isnone(self) -> bool:
        return self.isempty

    @staticmethod
    def merge_config_dict(left_dict: 'ConfigDict', right_dict: 'ConfigDict',
                          how='outer', how_section=None) -> 'ConfigDict':
        how_section = how if how_section is None else how_section
        keys, update = merge_dict_preprocessing(left_dict, right_dict, how=how)
        if not update:
            left_dict.clear()
            logger.debug("Left dict cleared.")
        for k in keys:
            if k in left_dict:  # Section already exists
                left_dict.get_section(k).merge(right_dict.get_section(k), how=how_section, inplace=True)
            else:
                left_dict.add_section(k, right_dict.get_section(k))
        logger.debug("Merge successful (ConfigDict method:  '{}', "
                     "SectionDict method: '{}') ok.".format(how, how_section))
        return left_dict

    def merge(self, config_dict: Union[dict, 'ConfigDict'], how='outer', how_section=None,
              inplace=False, deepcopy_right=True) -> Union['ConfigDict', None]:
        if not isinstance(config_dict, ConfigDict):
            config_dict = ConfigDict(config_dict)
        if config_dict is None:
            logger.error("bad type for config_dict")
            return None
        if inplace:
            left_dict = self
        else:
            left_dict = self.deepcopy()
        right_dict = config_dict.deepcopy() if deepcopy_right else config_dict
        n_config_dict = self.merge_config_dict(left_dict, right_dict, how=how, how_section=how_section)
        return None if inplace else n_config_dict

    def update(self, other: Union[dict, 'ConfigDict']) -> None:
        return self.merge(other, how='outer', how_section='outer', inplace=True)

    def append(self, other: Union[dict, 'ConfigDict']) -> None:
        return self.merge(other, how='append', how_section='append', inplace=True)
