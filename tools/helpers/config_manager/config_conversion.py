# open source
import ast
import re
import pandas as pd
from collections import OrderedDict

from tools.logger import logger
from tools.helpers.utils import isiterable
from tools.helpers.models import Reference, Path

DEFAULT_FLAG_START = r'@'
DEFAULT_FLAG_END = r'-'


def to_float(v, thousand_sep=None, decimal_sep=None):
    if thousand_sep:
        v = v.replace(thousand_sep, '')
    if decimal_sep:
        v = v.replace(decimal_sep, '.')
    return float(v)


def to_char(v):
    c = str(v)
    return c[0] if c else ''


def to_list(v, sep=','):  # deprecated, replaced by ast.literal_eval
    logger.debug("DeprecationWarning: to_list function is deprecated. You should use ast.literal_eval instead.")
    assert isinstance(sep, str)
    _s = str(v).strip().lstrip('[').rstrip(']').strip()
    _l = _s.split(sep)
    _l = [ele.strip() for ele in _l if ele]
    return _l


def to_tuple(v, sep=','):  # deprecated, replaced by ast.literal_eval
    return tuple(to_list(v, sep=sep))


def to_bool(v):
    if v in ("False", "None"):
        return False
    return bool(v)


AUTO_FLAG = 'auto'
CONVERSION_DICT = OrderedDict([
    # syntax: {prefix: (type, conversion_function_to_type), ...}
    # Conversions str <-> type
    ('b', (bool, to_bool)),
    ('d', (int, int)),
    ('i', (int, int)),
    ('ftws', (float, lambda v: to_float(v, thousand_sep=' '))),
    ('ftc', (float, lambda v: to_float(v, thousand_sep=','))),  # English format
    ('fdc', (float, lambda v: to_float(v, decimal_sep=','))),
    ('fdd', (float, lambda v: to_float(v, decimal_sep='.'))),
    ('ftwsdc', (float, lambda v: to_float(v, thousand_sep=' ', decimal_sep=','))),  # French format
    ('f', (float, to_float)),
    ('p', (Path, Path)),
    ('r', (Reference, Reference)),  # TODO
    ('c', (str, to_char)),
    ('s', (str, str)),
    ('date', (pd.Timestamp, pd.to_datetime)),
    ('datedb', (pd.Timestamp, lambda v: pd.to_datetime(v, dayfirst=True))),
    # Auto flag
    (AUTO_FLAG, (object, ast.literal_eval)),
    # Special conversions str -> list/tuple
    ('lc', (list, lambda v: to_list(v, sep=','))),
    ('lsc', (list, lambda v: to_list(v, sep=';'))),
    ('ls', (list, lambda v: to_list(v, sep='/'))),
    ('lbs', (list, lambda v: to_list(v, sep='\\'))),
    ('lnl', (list, lambda v: to_list(v, sep='\n'))),
    ('ld', (list, lambda v: to_list(v, sep='.'))),
    ('lws', (list, lambda v: to_list(v, sep=' '))),
    ('l', (list, to_list)),  # replaced by auto, more efficient.
    ('t', (tuple, to_tuple)),  # replaced by auto, more efficient.
])
FILE_TO_KEY = {k: v[1] for k, v in CONVERSION_DICT.items()}
KEY_TO_FILE = {v[0]: k for k, v in CONVERSION_DICT.items() if v[0] not in (list, tuple)}
KEY_TO_FILE.update({list: AUTO_FLAG, tuple: AUTO_FLAG})


def _add_flags_to_key(key, flags=None, start='@', end='-', **_kwargs):
    if flags is None:
        return key
    if isinstance(flags, str):
        flags = [flags]
    head = ""
    for flag in flags:
        head += "{}{}{}".format(start, flag, end)
    return head + key


def convert_dict_to_str(dico, auto=True, inplace=False):
    """Convert a dico (dictionary-like object) to make it writable to a file as text
    and easily loadable with the previous types, using convert_dict_from_str function.

    :param dico: dictionary-like object to convert. Flags are added to keys and values are casted to str.
    :param auto: if True, keys corresponding to complex objects get the flag 'auto'
    :param inplace: modify dico itself
    :return: dictionary-like object (same type as 'dico')

    >>> dico = {'a': True, 'b': False, 'c': None, 'd': [{(18, 3.1): 'a'}, 'end'], 'e': 9.9}
    >>> convert_dict_to_str(dico)
    {'@b-a': 'True', '@b-b': 'False', '@auto-c': 'None', '@auto-d': "[{(18, 3.1): 'a'}, 'end']", '@f-e': '9.9'}
    """
    n_dico = type(dico)()
    for k, v in dico.items():
        flag = KEY_TO_FILE.get(type(v), KEY_TO_FILE.get(object, None) if auto else None)
        n_k = _add_flags_to_key(k, flag)
        n_dico[n_k] = str(v)
    if inplace:
        dico.clear()
        dico.update(n_dico)
        return
    return n_dico


def _single_item_conversion(item, key=None, error='ignore', drop_none=False, drop_empty_iterable=False):
    if key is None:
        logger.debug("Conversion bypassed because argument 'key' is None. Returning None.")
        return item
    try:
        if item is None:
            return None
        if isiterable(item):  # if iterable object
            _v = type(item)(_single_item_conversion(s_item, key=key, error=error,
                                                    drop_none=drop_none, drop_empty_iterable=drop_empty_iterable)
                            for s_item in item)
        else:
            _v = FILE_TO_KEY.get(key, str)(item)

        if drop_none and isiterable(_v):
            _v = type(_v)(s_item for s_item in _v if s_item is not None)
        if drop_empty_iterable and not _v:
            _v = None
    except (ValueError, TypeError, SyntaxError) as err:
        if error == 'ignore':
            logger.debug("Conversion error with flag 'ignore'. Returning the original string '{}'.".format(item))
            return item
        elif error == 'drop':
            logger.debug("Conversion error with flag 'drop'. Returning None value (original string: '{}'.".format(item))
            return None
        elif error == 'auto-conversion':
            try:
                n_item = ast.literal_eval(item)
                logger.debug("Conversion error with flag 'auto-conversion'. "
                             "Returning the evaluation of string '{}'.".format(item))
                return n_item
            except (ValueError, SyntaxError):
                logger.debug("Conversion error with flag 'auto-conversion'. Auto-conversion failed."
                             "Returning the original string '{}'.".format(item))
                return item
        else:
            logger.exception(err)
            logger.debug("Conversion error with flag 'error'. The original string was '{}'.".format(item))
            raise err.__class__(err)
    return _v


def _multiple_item_conversion(item, flags=None, error='ignore', drop_none=False, drop_empty_iterable=False,
                              ascendant=False):
    if not flags:
        return item
    if ascendant:
        flags.reverse()
    if not isinstance(flags, (tuple, list)):
        raise TypeError("Type '{}' of flags argument '{}' is not taken in charge.".format(type(flags), flags))
    return _process_multiple_item_conversion(item, flags=flags, error=error,
                                             drop_none=drop_none, drop_empty_iterable=drop_empty_iterable)


def _process_multiple_item_conversion(item, flags=None, error='ignore',
                                      drop_none=False, drop_empty_iterable=False):
    if len(flags) == 1:
        return _single_item_conversion(item, flags[0], error=error,
                                       drop_none=drop_none, drop_empty_iterable=drop_empty_iterable)
    else:
        return _single_item_conversion(
            _process_multiple_item_conversion(item, flags[:-1], error=error,
                                              drop_none=drop_none, drop_empty_iterable=drop_empty_iterable),
            flags[-1], error=error, drop_none=drop_none, drop_empty_iterable=drop_empty_iterable)


def _parse_key(key, pattern=r'^[{}]([a-z0-9]+)[{}]', start=DEFAULT_FLAG_START, end=DEFAULT_FLAG_END, **_kwargs):
    ptrn = pattern.format(start, end)
    regex = re.compile(ptrn)
    flags = []  # list of flags
    found = 1
    while found:
        flags += regex.findall(key)
        key, found = regex.subn("", key)
    flags = flags or None
    return key, flags


def _no_flag_handling(key, no_flag='ignore'):
    if no_flag == 'ignore':
        return []
    elif no_flag == 'drop':
        logger.debug("Key '{}' will be dropped because it has no flag.".format(key))
        return None
    elif no_flag == 'auto-conversion':
        logger.debug("Auto conversion will be performed for key '{}' because it has no flag.".format(key))
        return [AUTO_FLAG]
    else:
        err_msg = "No flag for the key '{}'".format(key)
        logger.error(err_msg)
        raise ValueError(err_msg)


def _handle_duplicates(dico, key, value, flag='first', inplace=False):
    """Handle duplicates in dico.

    :param dico: dico to update
    :param key: key to check
    :param value: value to set
    :param flag: 'first', 'last', 'rename' or 'error' (or whatever, which means 'error')
    :param inplace: modification of dico inplace if True
    :return: None if inplace is True, else dico updated
    """
    n_dico = type(dico)()
    if key in dico:
        logger.debug("Key '{}' is duplicated.".format(key))
        if flag == 'first':
            pass
        elif flag == 'last':
            n_dico[key] = value
        elif flag == 'rename':
            i = 0
            exists = True
            while exists:
                i += 1
                n_key = "{}_{}".format(key, i)
                exists = True if n_key in dico else False
            n_dico[n_key] = value
        else:
            err_msg = "Duplicate keys '{}' found! Conversion process aborting."
            logger.error(err_msg)
            raise ValueError(err_msg)
    else:
        n_dico[key] = value
    if inplace:
        dico.update(n_dico)
        return
    return n_dico


def convert_dict_from_str(dico, allow_multiple=True, error='ignore', drop_none=False,
                          drop_empty_iterable=False, ascendant=False, no_flag='ignore',
                          inplace=False, duplicates='first', **parser_cfg):
    """Convert a dict of str (generated from a file for example) to a typed dict.
    Simple types that can be recognised: str, bool, int, float, list, tuple.
    Custom classes: Reference, Path
    Advanced types (with 'auto' flag): expressions with dict, set, bytes, None and simple types.

    :param dico: dictionary-like object to convert with keys and values of type 'str'.
    :param allow_multiple: if True, multiple flags are allowed (applied from left to right)
    :param error: behavior on casting error. Possible values:
                    'ignore' (returns the initial string),
                    'drop' (returns None),
                    'error' (raise an error if casting fails),
                    'auto-conversion' (try to convert automatically; if it fails, returns the initial string)
    :param drop_none: if True, None values are dropped
    :param drop_empty_iterable: if True, empty iterable objects (list, tuple) are dropped
    :param ascendant: if True, the flags are applied from the last to the first
    :param no_flag: behavior if no flag found. 'ignore', 'error', 'drop', 'auto-conversion'
    :param inplace: returns dico inplace
    :param duplicates: behavior if duplicates found. 'drop', 'first', 'last', 'error'.
    :param parser_cfg: kwargs for _parse_key function
    :return: dictionary-like object (same type as 'dico')

    # Simple test
    >>> test_dict = {"a": "without_flag", "@i-b": "1", "@f-c": "9.2", "@b-d": "", "@b-e": "5",  "@b-f": "False"}
    >>> convert_dict_from_str(test_dict)
    {'a': 'without_flag', 'b': 1, 'c': 9.2, 'd': False, 'e': True, 'f': False}

    # Numbers test
    >>> num_dict = {"@f-d1": "1.6", "@i-d2": "1.7", "@f-@i-d3": "1.8", "@i-@f-d4": "1.9", "d5": 2.0, "@ftwsdc-d6": "2 252,9"}
    >>> convert_dict_from_str(num_dict)
    {'d1': 1.6, 'd2': '1.7', 'd3': 1, 'd4': 1.9, 'd5': 2.0, 'd6': 2252.9}

    # Duplicates handling test
    >>> dup_dict = OrderedDict([("@s-overwritten", "value1"), ("overwritten", "value2"), ("@auto-overwritten", "value3")])
    >>> convert_dict_from_str(dup_dict, duplicates='rename')
    OrderedDict([('overwritten', 'value1'), ('overwritten_1', 'value2'), ('overwritten_2', 'value3')])
    >>> convert_dict_from_str(dup_dict, duplicates='first')
    OrderedDict([('overwritten', 'value1')])
    >>> convert_dict_from_str(dup_dict, duplicates='last')
    OrderedDict([('overwritten', 'value3')])

    # Date test
    >>> date_dict = {"@date-date": "2019-04-01", "@date-date2": "04-13-2018", "@date-date3": "13/04/2018"}
    >>> convert_dict_from_str(date_dict)
    {'date': Timestamp('2019-04-01 00:00:00'), 'date2': Timestamp('2018-04-13 00:00:00'), 'date3': Timestamp('2018-04-13 00:00:00')}
    >>> date_special_dict = {"@date-date_std": "04/11/2018", "@datedb-date_day_before": "04/11/2018"}
    >>> convert_dict_from_str(date_special_dict)
    {'date_std': Timestamp('2018-04-11 00:00:00'), 'date_day_before': Timestamp('2018-11-04 00:00:00')}

    # List test
    >>> list_dict = {"@auto-list1": "[18, 13]", "@l-list2": "[19, 13]", "@auto-list3": "[{(18, 13): 'a'}, 'end']"}
    >>> convert_dict_from_str(list_dict)
    {'list1': [18, 13], 'list2': ['19', '13'], 'list3': [{(18, 13): 'a'}, 'end']}

    # Auto conversion test
    >>> auto_dict = {"a": "True", "b": "False", "c": "None", "d": "[{(18, 13): 'a'}, 'end']", "e": '9.9', "f": 9.9}
    >>> convert_dict_from_str(auto_dict, no_flag="auto-conversion")
    {'a': True, 'b': False, 'c': None, 'd': [{(18, 13): 'a'}, 'end'], 'e': 9.9, 'f': 9.9}
    """
    # It is supposed that all keys are lower case!
    # If some keys are identical, only one will be retained (the last), others will be overwritten!
    if dico is None:
        logger.warning("none as dict")
        return None
    n_dico = type(dico)()
    for k, v in dico.items():
        n_k, flags = _parse_key(k, **parser_cfg)
        if not allow_multiple:
            flags = flags[0] if flags else None
        if not flags:
            flags = _no_flag_handling(k, no_flag=no_flag)
            if flags is None:
                continue
        n_v = _multiple_item_conversion(v, flags, error=error, drop_none=drop_none,
                                        drop_empty_iterable=drop_empty_iterable, ascendant=ascendant)
        if n_v is not None or not drop_none:
            _handle_duplicates(n_dico, n_k, n_v, duplicates, inplace=True)
    if inplace:
        dico.clear()
        dico.update(n_dico)
        return
    return n_dico
