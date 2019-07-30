# -*- coding: utf-8 -*-
# open source project
"""
Metaclasses

The syntax to use a metaclass in Python 3 is as follows:

class MyClass(metaclass=MyMetaClass):
    pass
"""


class Singleton(type):
    """Metaclass that authorize only one instance of a class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LockChangeAttr(type):
    """Metaclass that locks attribute modification after a certain limit"""
    # WARN: Metaclass attributes must be immutable to avoid modifications inplace by instantiated classes.
    _modification_count = None  # immutable
    _modification_limit = 1  # immutable
    _attr_exceptions = tuple()  # immutable and iterable

    def __setattr__(cls, key, value):
        if cls._modification_count is None:
            super(LockChangeAttr, cls).__setattr__('_modification_count', {})
        if cls not in cls._modification_count:
            cls._modification_count[cls] = {}
        if key not in cls._modification_count[cls]:
            cls._modification_count[cls][key] = 0
        cls._modification_count[cls][key] += 1
        if (cls._modification_count[cls][key] > cls._modification_limit
                and key not in cls._attr_exceptions):
            print("WARNING: modification of attribute '{}' has reached its limit ({})".format(key,
                                                                                              cls._modification_limit))
            return
        return super(LockChangeAttr, cls).__setattr__(key, value)


def lock_change_attr_metaclass(modification_limit=1, attr_exceptions=tuple()):
    """Returns a custom metaclass inherited from LockChangeAttr

    :param modification_limit: number of times an attribute can be modified
    :param attr_exceptions: iterable of attributes that can be modified without any limit
    """

    class CustomLockChangeAttr(LockChangeAttr):
        _modification_count = None
        _modification_limit = modification_limit
        _attr_exceptions = attr_exceptions

    return CustomLockChangeAttr
