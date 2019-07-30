# -*- coding: utf-8 -*-
# open source project
"""
Dictionary-like classes
"""
from collections import UserDict, OrderedDict
from copy import copy, deepcopy


class IdentityDict(UserDict):
    """Dict which returns the key if key not in dict when getting item.
     If 'func' arg is set, the function 'func' is applied to key before return"""
    def __init__(self, *args, **kwargs):
        self._func = kwargs.pop('func', lambda x: x)
        super().__init__(*args, **kwargs)

    def __getitem__(self, item):
        if item in self:
            return super().__getitem__(item)
        return self._func(item)


class BaseDict:
    """Base class of ordered-dictionary-like objects where keys have a specified format."""
    TO_KEY_FUNC = lambda _, x: x  # function to convert a key to a specified format
    _DEFAULT_DICT = OrderedDict

    def __init__(self, *args, **kwargs):
        dico = self._DEFAULT_DICT(*args, **kwargs)
        dico = self._DEFAULT_DICT([(self.TO_KEY_FUNC(k), v) for k, v in dico.items()])  # convert keys
        self._cfg = dico

    def __repr__(self):
        return "{}:\n{}".format(self.__class__.__name__, self._cfg)

    def __iter__(self):
        for key in self._cfg:
            yield key

    def __contains__(self, item):
        return self.TO_KEY_FUNC(item) in self.keys()  # or item in self.keys()

    def __len__(self):
        return len(self._cfg)

    def __getitem__(self, item):
        n_item = self.TO_KEY_FUNC(item)
        return self._cfg[n_item]

    def __setitem__(self, key, value):
        n_key = self.TO_KEY_FUNC(key)
        self._cfg[n_key] = value

    def __eq__(self, other):
        return self._cfg == other

    # "Inherited" from dict
    @classmethod
    def fromkeys(cls, *args, **kwargs):
        n_dict = cls._DEFAULT_DICT.fromkeys(*args, **kwargs)
        return cls(n_dict)

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

    # "Inherited" from OrderedDict
    def move_to_end(self, key):
        key = self.TO_KEY_FUNC(key)
        return self._cfg.move_to_end(key)

    # Inspired by pandas dataframe
    @classmethod
    def from_dict(cls, dico):
        return cls(dico)
