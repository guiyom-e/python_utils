# -*- coding: utf-8 -*-
# open source project
"""
Classes inherited from string ("Custom strings") and from list ("Collections").
"""
from tools import logger
from tools.helpers import isiterable
from tools.helpers.models.types_models import keep_type


class _CustomStr(str):
    """string-like object with some enhanced functions"""
    _SETTABLE_ATTR = ['_data']  # Allowed attributes to be set once after __new__ is called.
    _ALLOW_CASTING = True  # Allow non-string objects to be casted.
    _ALLOW_MULTIPLE = False  # Allow collections of objects. Priority over _ALLOW_CASTING
    _SILENT_ERROR = False  # __new__ errors are silent, bad data are replaced by None

    def __new__(cls, *args, **kwargs):
        if (len(args) > 1) or (len(kwargs) > 1) or (args and kwargs):
            raise TypeError("'{}'() takes 1 positional argument but {} were given"
                            .format(cls.__name__, len(args) + len(kwargs)))
        data = args[0] if args else kwargs.popitem()[1] if kwargs else None
        data = cls._check_input(data)
        data = cls._check_data(data)
        obj = str.__new__(cls, '' if data is None else data)
        obj._data = data
        return obj

    @classmethod
    def _check_input(cls, data):  # should not be overwritten, prefer _check_data
        if isinstance(data, cls):
            return data._data
        elif isinstance(data, str) or data is None:
            return data
        elif isiterable(data) and cls._ALLOW_MULTIPLE or cls._ALLOW_CASTING:
            return data
        elif cls._SILENT_ERROR:
            return None
        else:
            msg = "argument should be a path-like object or str, not '{}'".format(type(data))
            logger.error(msg)
            raise TypeError(msg)

    @classmethod
    def _check_data(cls, data):  # can  be overwritten
        return data

    def __str__(self):
        return '' if self._data is None else self._data

    def __repr__(self):
        return "{}: {}".format(self.__class__.__name__, self._data)

    def __eq__(self, other):
        return self._data == other

    def __hash__(self):
        return self._data.__hash__()  # ok since str and None are hashable

    def __setattr__(self, key, value):
        if key in self._SETTABLE_ATTR and key not in dir(self):
            return super().__setattr__(key, value)
        if key in dir(self):
            raise AttributeError("'{}' object attribute '{}' is read - only".format(type(key), key))
        else:
            raise AttributeError("'{}' object has no attribute '{}'".format(type(key), key))

    @property
    def isnone(self) -> bool:
        return self._data is None

    # Returning class objects
    @keep_type()
    def format(self, *args, **kwargs):
        return super().format(*args, **kwargs)

    @keep_type()
    def upper(self, *args, **kwargs):
        return super().upper(*args, **kwargs)

    @keep_type()
    def lower(self, *args, **kwargs):
        return super().lower(*args, **kwargs)

    @keep_type()
    def swapcase(self, *args, **kwargs):
        return super().swapcase(*args, **kwargs)

    @keep_type()
    def join(self, *args, **kwargs):
        return super().join(*args, **kwargs)

    @keep_type()
    def title(self, *args, **kwargs):
        return super().title(*args, **kwargs)

    @keep_type()
    def capitalize(self, *args, **kwargs):
        return super().capitalize(*args, **kwargs)

    @keep_type()
    def strip(self, *args, **kwargs):
        return super().strip(*args, **kwargs)

    @keep_type()
    def lstrip(self, *args, **kwargs):
        return super().lstrip(*args, **kwargs)

    @keep_type()
    def rstrip(self, *args, **kwargs):
        return super().rstrip(*args, **kwargs)

    @keep_type()
    def replace(self, *args, **kwargs):
        return super().replace(*args, **kwargs)
    # TODO: add more methods


class _CollectionCustomStr(list):  # Collection (list) of _CustomStr objects (1 dimension only)
    """list-like model which permit to apply methods to every element in the object.

    >>> a = _CollectionCustomStr(['a', 'b', 'c'])
    >>> a
    [_CustomStr: a, _CustomStr: b, _CustomStr: c]
    >>> a.append('abc')  # list behavior
    >>> a
    [_CustomStr: a, _CustomStr: b, _CustomStr: c, _CustomStr: abc]
    >>> a.upper()  # string behavior
    [_CustomStr: A, _CustomStr: B, _CustomStr: C, _CustomStr: ABC]
    >>> a.count('a')  # priority to list methods
    1
    """
    _STR_CLS = _CustomStr

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for i, ele in enumerate(self):
            self[i] = self._STR_CLS(ele)

    def __str__(self):
        return str([str(ele) for ele in self])

    def __getattr__(self, item):
        if item in dir(self._STR_CLS):
            obj = getattr(self._STR_CLS, item)
            keep_coll = not (not hasattr(obj, 'keep_type') or not obj.keep_type)
            if not callable(getattr(self._STR_CLS, item)):  # attribute or property
                res = [getattr(ele, item) for ele in self]
                return self.__class__(res) if keep_coll else res

            def method(*args, **kwargs):  # method
                res = [getattr(ele, item)(*args, **kwargs) for ele in self]
                return self.__class__(res) if keep_coll else res

            return method
        return self.__getattribute__(item)

    def __add__(self, other):
        if isinstance(other, str):
            return self.__class__([ele + self._STR_CLS(other) for ele in self])
        if not isinstance(other, list):
            err_msg = "can only concatenate list objects (not '{}') to {}".format(type(other), self.__class__.__name__)
            raise TypeError(err_msg)
        other = [self._STR_CLS(ele) for ele in other]
        return super().__add__(other)

    def __radd__(self, other):
        if isinstance(other, str):
            return self.__class__([self._STR_CLS(other) + ele for ele in self])
        if not isinstance(other, list):
            err_msg = "can only concatenate list objects (not '{}') to {}".format(type(other), self.__class__.__name__)
            raise TypeError(err_msg)
        other = [self._STR_CLS(ele) for ele in other]
        return self.__class__(other + self)

    def __getitem__(self, item):
        if isinstance(item, slice):
            return self.__class__(self.__getitem__(item))
        return super().__getitem__(item)

    def copy(self):
        return self.__class__(super().copy())

    def append(self, obj) -> None:
        obj = self._STR_CLS(obj)
        super().append(obj)

    def extend(self, iterable) -> None:
        iterable = [self._STR_CLS(ele) for ele in iterable]
        super().extend(iterable)

    def insert(self, index: int, obj) -> None:
        obj = self._STR_CLS(obj)
        super().insert(index, obj)


class _DynamicCustomStr(_CustomStr):  # Allow iterable inputs
    """Depending on argument passed when calling the class, create a _CustomStr object or a _CollectionCustomStr.

    If an 'iterable' (i.e. if isiterable(obj) is True) is passed to the constructor,
    a _CollectionCustomStr-like collection of _CustomStr-like objects is created.

    If an other object is passed to the constructor, a _CustomStr-like object is created.

    It is possible to inherit from this class.

    Examples below show inheritances and types of created objects.

    # Default behavior

    >>> _DynamicCustomStr('abc')
    _DynamicCustomStr: abc
    >>> _DynamicCustomStr(['abc'])
    [_DynamicCustomStr: abc]
    >>> _CollectionCustomStr(['abc'])
    [_CustomStr: abc]

    # Types

    >>> isinstance(_DynamicCustomStr('abc'), _DynamicCustomStr)
    True
    >>> isinstance(_DynamicCustomStr('abc'), _CustomStr)
    True
    >>> isinstance(_DynamicCustomStr(['abc']), _DynamicCustomStr)
    False
    >>> isinstance(_DynamicCustomStr(['abc']), _CollectionCustomStr)
    True
    >>> isinstance(_DynamicCustomStr(['abc'])[0], _DynamicCustomStr)
    True
    >>> isinstance(_DynamicCustomStr(['abc'])[0], _CustomStr)
    True

    ################
    # Inheritances #
    ################
    # 1st case: not modifying inplace the associated collection (_MODIFY_COLLECTION_INPLACE is False)

    >>> class OtherDynamicCS(_DynamicCustomStr): pass
    >>> OtherDynamicCS('abc')
    OtherDynamicCS: abc
    >>> OtherDynamicCS(['abc'])
    [OtherDynamicCS: abc]
    >>> _CollectionCustomStr(['abc'])  # still the same behavior
    [_CustomStr: abc]

    # Collections classes are independent

    >>> OtherDynamicCS._DYNAMIC_COLLECTIONS[OtherDynamicCS]
    <class 'str_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
    >>> OtherDynamicCS._DYNAMIC_COLLECTIONS[_DynamicCustomStr]
    <class 'str_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
    >>> OtherDynamicCS._DYNAMIC_COLLECTIONS[OtherDynamicCS] == OtherDynamicCS._DYNAMIC_COLLECTIONS[_DynamicCustomStr]
    False

    >>> OtherDynamicCS._COLLECTION_CLS is _CollectionCustomStr
    True
    >>> OtherDynamicCS._DYNAMIC_COLLECTIONS[OtherDynamicCS] is _CollectionCustomStr
    False

    >>> type(OtherDynamicCS(['abc'])) == type(_DynamicCustomStr(['abc']))
    False
    >>> type(OtherDynamicCS(['abc'])) is type(_CollectionCustomStr(['abc']))
    False

    # 2nd case: modifying inplace the associated collection by setting _MODIFY_COLLECTION_INPLACE to True:
    # WARNING: risky behavior if no initialization!

    >>> class FrozenDynamicCS(_DynamicCustomStr):_MODIFY_COLLECTION_INPLACE = True
    >>> _CollectionCustomStr(['abc'])  # _CollectionCustomStr has the same behavior as before
    [_CustomStr: abc]
    >>> FrozenDynamicCS('abc')
    FrozenDynamicCS: abc
    >>> FrozenDynamicCS(['abc'])
    [FrozenDynamicCS: abc]
    >>> _CollectionCustomStr(['abc'])  # change: _CollectionCustomStr has been modified inplace
    [FrozenDynamicCS: abc]

    # Collections classes are dependent

    >>> FrozenDynamicCS._DYNAMIC_COLLECTIONS[FrozenDynamicCS]
    <class 'str_models._CollectionCustomStr'>
    >>> FrozenDynamicCS._DYNAMIC_COLLECTIONS[_DynamicCustomStr]  # still stored in the
    <class 'str_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
    >>> FrozenDynamicCS._DYNAMIC_COLLECTIONS[FrozenDynamicCS] == _CollectionCustomStr
    True

    >>> FrozenDynamicCS._COLLECTION_CLS is _CollectionCustomStr  # same
    True
    >>> FrozenDynamicCS._DYNAMIC_COLLECTIONS[FrozenDynamicCS] is _CollectionCustomStr  # different
    True

    # _DynamicCustomStr not changed because initialized before

    >>> type(FrozenDynamicCS(['abc'])) is type(_DynamicCustomStr(['abc']))
    False
    >>> type(FrozenDynamicCS(['abc'])) is type(_CollectionCustomStr(['abc']))  # _CollectionCustomStr modified inplace
    True
    """
    _COLLECTION_CLS = _CollectionCustomStr
    _ALLOW_MULTIPLE = True  # Allow collections of objects. Priority over _ALLOW_CASTING
    _DYNAMIC_COLLECTIONS = {}
    _MODIFY_COLLECTION_INPLACE = False

    # if True, _COLLECTION_CLS._STR_CLS will be defined to this class, when the first object is created.

    def __new__(cls, *args, **kwargs):
        """Create a new object, whether inherited from _CustomStr or _CollectionCustomStr."""
        if (len(args) > 1) or (len(kwargs) > 1) or (args and kwargs):
            raise TypeError("'{}'() takes 1 positional argument but {} were given"
                            .format(cls.__name__, len(args) + len(kwargs)))
        data = args[0] if args else kwargs.popitem()[1] if kwargs else None
        data = cls._check_input(data)
        if isiterable(data):  # create a collection of _CustomStr
            return cls._get_dynamic_collection()(data)

        return _CustomStr.__new__(cls, data)

    @classmethod
    def _get_dynamic_collection(cls):
        if cls in cls._DYNAMIC_COLLECTIONS:
            return cls._DYNAMIC_COLLECTIONS[cls]
        if cls._MODIFY_COLLECTION_INPLACE:
            cls._COLLECTION_CLS._STR_CLS = cls
            cls._DYNAMIC_COLLECTIONS[cls] = cls._COLLECTION_CLS
            return cls._COLLECTION_CLS
        else:
            class _DynamicCollectionCustomStr(cls._COLLECTION_CLS):
                _STR_CLS = cls

            cls._DYNAMIC_COLLECTIONS[cls] = _DynamicCollectionCustomStr
            return _DynamicCollectionCustomStr
