# open source
from typing import Tuple, KeysView, Union

import numpy as np
import pandas as pd

from tools.logger import logger


def isiterable(obj):
    # return '__iter__' in dir(obj)  # can be misleading because str objects are iterable.
    return isinstance(obj, (tuple, list, set))


def isinstance_filetypes(filetypes):
    """Returns True if 'filetypes' is a valid variable for filetypes argument
    in tkinter.filedialog functions, else False."""
    if not isinstance(filetypes, (list, tuple, set)):
        return False
    for filetype in filetypes:
        if not isinstance(filetype, tuple):
            return False
        if len(filetype) != 2:
            return False
    return True


def shorten_dataframe_str(df: pd.DataFrame, column_name: str, max_length: int,
                          replacement_str: str = '...', inplace: bool = False) -> pd.DataFrame:
    """Shorten string values that are longer than 'max_length' in column 'column_name'.
    If some values are not strings, they are converted.

    >>> df = pd.DataFrame(columns=["a", "b"], data=[["baobab", "octopus"], ["birthday", "mark"], [1, 2]])
    >>> shorten_dataframe_str(df, 'a', 6)
               a        b
    0     baobab  octopus
    1  birthd...     mark
    2          1        2


    :param df: pandas dataframe
    :param column_name: column name of dataframe df
    :param max_length: maximum length of strings
    :param replacement_str: string to append to the cut strings. Default: '...'
    :param inplace: if True, the input dataframe is modified inplace
    :return: dataframe modified
    """
    if not inplace:
        df = df.copy()
    df.loc[df[column_name].apply(lambda x: len(str(x))) > max_length, column_name] \
        = df[column_name].apply(lambda x: '{}{}'.format(str(x)[:max_length], replacement_str))
    return df


def merge_dict_preprocessing(left_dict: dict, right_dict: dict,
                             how: str = 'outer') -> Union[Tuple[Union[set, KeysView], Union[bool]], Tuple[None, None]]:
    """Returns the tuple (keys, update) which permit to update a 'left_dict' with a 'right_dict' with the method 'how'.

    Examples:
    >>> left_dict, right_dict = {1: "a", 2: "b", 3: "c"}, {1: "d", 4: "e"}
    >>> merge_dict_preprocessing(left_dict, right_dict, how='left')
    ({1}, True)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='inner')
    ({1}, False)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='right_anti')
    ({4}, False)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='right')
    (dict_keys([1, 4]), False)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='outer')
    (dict_keys([1, 4]), True)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='append')
    ({4}, True)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='none')
    (set(), True)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='clear')
    (set(), False)
    >>> merge_dict_preprocessing(left_dict, right_dict, how='bad_string')
    (None, None)

    Example of use:
    >>> keys, update = merge_dict_preprocessing(left_dict, right_dict, how='outer')
    >>> if not update: left_dict.clear()
    >>> left_dict.update([(k, right_dict[k]) for k in keys])
    >>> left_dict
    {1: 'd', 2: 'b', 3: 'c', 4: 'e'}

    :param left_dict: left dictionary-like object
    :param right_dict: right dictionary-like object
    Dictionary-like object need the methods 'keys' which returns a set-like object
    with methods '__sub__' and '__and__'.
    :param how: - 'left': only right_dict keys already in left_dict will be updated.
                - 'inner': only keys in self AND right_dict will be kept.
                - 'right_anti': only keys in right_dict AND NOT in left_dict.
                - 'right' or 'replace': only right_dict keys will be kept.
                - 'outer'or 'update': all keys of self AND right_dict will be kept.
                - 'append': append new keys of right_dict, but don't modify existing keys in left_dict.
                - 'none' or None: no modification
                - 'clear': clear left_dict
    :return: keys (set), update (bool)
    """
    if how == 'left':  # only right_dict keys already in left_dict will be updated.
        keys = left_dict.keys() & right_dict.keys()
        update = True
    elif how == 'inner':  # only keys in self AND right_dict will be kept.
        keys = left_dict.keys() & right_dict.keys()
        update = False
    elif how in ['rightanti', 'right_anti']:  # only keys in right_dict AND NOT in left_dict
        keys = right_dict.keys() - left_dict.keys()
        update = False
    elif how in ['right', 'replace']:  # only right_dict keys will be kept. Equivalent to replace.
        keys = right_dict.keys()
        update = False
    elif how in ['outer', 'update']:  # all keys of self AND right_dict will be kept. Equivalent to update.
        keys = right_dict.keys()
        update = True
    elif how == 'append':  # append new keys of right_dict, but don't modify existing keys in left_dict.
        keys = right_dict.keys() - left_dict.keys()
        update = True
    elif how in ['none', None]:  # no modification
        keys = set()
        update = True
    elif how == 'clear':
        keys = set()
        update = False
    else:
        logger.error("Bad 'how' argument '{}'. Expected 'left', 'inner', 'right_anti', "
                     "'right', 'outer', 'append', 'none' or 'clear".format(how))
        return None, None
    return keys, update


def coordinates_to_distance(lat1, lon1, lat2, lon2):
    """Compute the approximate distance between two points of coordinates (lat1, log1), (lat2, long2).
    Formula adapted from https://en.wikipedia.org/wiki/Haversine_formula"""
    radius = 6378.137  # Radius of earth in KM
    d_lat = lat2 * np.pi / 180 - lat1 * np.pi / 180
    d_lon = lon2 * np.pi / 180 - lon1 * np.pi / 180
    a = np.sin(d_lat / 2) * np.sin(d_lat / 2) + \
        np.cos(lat1 * np.pi / 180) * np.cos(lat2 * np.pi / 180) * \
        np.sin(d_lon / 2) * np.sin(d_lon / 2)
    c = 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
    d = radius * c
    return d
