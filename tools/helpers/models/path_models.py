# open source
import os
from typing import Tuple
from copy import copy, deepcopy
import functools

from tools.logger import logger

from tools.helpers.models.metaclasses import LockChangeAttr
from tools.helpers.models.types_models import Property
from tools.helpers.utils import isiterable


def add_tag(tag='tag', tag_value=True):
    """Set an attribute to a function."""
    def decorator(func):
        if type(func) is property:
            wrapper = Property(func.fget, func.fset, func.fdel, func.__doc__)
            wrapper.__setattr__(tag, tag_value)
            return wrapper

        func.__setattr__(tag, tag_value)
        return func
    return decorator


def keep_type(func_type='function'):
    """Set the attribute 'keep_type' to a method or property and convert result to original class.

    Handle functions, methods, properties, class methods.
    """
    flag = 'function'
    if func_type in {classmethod, 'classmethod'}:
        flag = 'classmethod'
    elif func_type in {staticmethod, 'staticmethod'}:
        flag = 'staticmethod'
    elif func_type in {property, 'property'}:
        flag = 'property'

    def decorator(func):
        if type(func) is staticmethod or flag == 'staticmethod':
            raise TypeError("keep_type decorator can not be applied to staticmethod descriptors")

        def wrapper1(self, *args, **kwargs):
            if type(func) is property:
                res = func.__get__(self)
            else:
                res = func(self, *args, **kwargs)
            if flag == 'classmethod':
                return self(res)
            return self.__class__(res)
        if type(func) is property:
            wrapper1 = property(wrapper1, func.fset, func.fdel, func.__doc__)
        elif flag == 'property':
            wrapper1 = property(wrapper1, None, None, func.__doc__)
        else:
            functools.update_wrapper(wrapper1, func)

        wrapper2 = add_tag(tag='keep_type')(wrapper1)
        if flag == 'classmethod':
            wrapper2 = classmethod(wrapper2)
        return wrapper2
    return decorator


class TestKeepType:
    def __init__(self, *args):
        if args:
            self.disp = args[0]
        else:
            self.disp = 8
        print('init: {}'.format(args))
        super().__init__()

    def __repr__(self):
        return super().__repr__() + "_{}".format(self.disp)

    @keep_type()
    @property
    def a1(self):
        return 4

    @keep_type(property)
    def a2(self):
        return 4

    @keep_type()
    def b(self):
        return 5

    # buggy
    @classmethod
    @keep_type()
    def c1(cls):
        return 6

    @keep_type('classmethod')
    def c2(cls):
        return 6

    @staticmethod
    @keep_type
    def d():
        return 7


class _CustomStr(str):
    """str-like object with some enhanced functions"""
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
    """list-like model which permit to apply methods to every element in the object"""
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
    <class 'path_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
    >>> OtherDynamicCS._DYNAMIC_COLLECTIONS[_DynamicCustomStr]
    <class 'path_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
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
    <class 'path_models._CollectionCustomStr'>
    >>> FrozenDynamicCS._DYNAMIC_COLLECTIONS[_DynamicCustomStr]  # still stored in the
    <class 'path_models._DynamicCustomStr._get_dynamic_collection.<locals>._DynamicCollectionCustomStr'>
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


class FileExt(_CustomStr):  # not dynamic
    """File extension class model"""
    EXT_SEP = os.extsep  # standard extension separator is '.'

    @classmethod
    def _check_data(cls, data):
        if data is None:
            # logger.warning("None extension is not recommended. Please use an empty string '' to mean no extension.")
            return None
        if not data.startswith(cls.EXT_SEP):
            data = cls.EXT_SEP + data
        return data

    def __eq__(self, other):
        return self._data == FileExt(other)._data

    @property
    def isempty(self):
        return self._data is None


class DefaultFiletypesDict:
    def __init__(self, dico=None, all_files=True):
        self._dico = dico or {}
        self._all_files = bool(all_files)

    def __getitem__(self, item):
        if item in self:
            return self._dico[item]
        item = FileExt(item)
        if item.isempty:
            return [('all_files', '*.*')] if self._all_files else None
        if self._all_files:
            return [('{} file'.format(item), '*{}'.format(item))]
        else:
            return [('{} file'.format(item), '*{}'.format(item)), ('all_files', '*.*')]

    def get(self, key, default=None):
        if key in self:
            return self[key]
        return default

    def __iter__(self):
        for k in self._dico:
            yield k


class _BasePath(_DynamicCustomStr):
    """Path model class where methods and properties are defined."""
    _ALLOW_MULTIPLE = False  # Allow collections of objects: no.
    _ALLOW_CASTING = False  # Allow non-string objects to be casted: no.
    _FILE_EXT_CLS = FileExt

    # Path properties
    @property
    def path(self) -> str:
        return self._data or ''

    @keep_type(property)
    def abspath(self) -> '_BasePath':
        return os.path.abspath(self.path)

    @property
    def exists(self) -> bool:
        return os.path.exists(self.path)

    @property
    def isempty(self) -> bool:
        return self.isnone

    @property
    def isfile(self) -> bool:
        return os.path.isfile(self.path)

    @property
    def isdir(self) -> bool:
        return os.path.isdir(self.path)

    @property
    def isabs(self) -> bool:
        return os.path.isabs(self.path)

    @keep_type(property)
    def split_path(self) -> Tuple['_BasePath', '_BasePath']:  # not real output
        dirname, filename = os.path.split(self.path)
        return dirname, filename

    @property
    def splitext(self) -> Tuple['_BasePath', _FILE_EXT_CLS]:
        radix, ext = os.path.splitext(self.path)
        return self.__class__(radix), self._FILE_EXT_CLS(ext)

    @keep_type(property)
    def dirname(self) -> '_BasePath':
        return os.path.dirname(self.path)
        # return self.split_path[0]  # should be equivalent

    @keep_type(property)
    def filename(self) -> '_BasePath':
        return self.split_path[1]

    @property
    def ext(self) -> _FILE_EXT_CLS:
        return self.splitext[1]

    @property
    def extension(self) -> _FILE_EXT_CLS:
        return self.ext

    @keep_type(property)
    def radix(self) -> '_BasePath':
        return self.splitext[0]

    @keep_type(property)
    def basis(self) -> '_BasePath':
        return self.radix

    @keep_type(property)
    def filename_radix(self) -> '_BasePath':
        return self.filename.radix

    @keep_type(property)
    def filename_basis(self) -> '_BasePath':
        return self.filename_radix

    @keep_type(property)
    def parent_dirname(self) -> '_BasePath':
        return self.dirname.dirname

    @keep_type(property)
    def short_dirname(self) -> '_BasePath':
        return self.dirname.split_path[-1]

    @keep_type()
    def join_path(self, other) -> '_BasePath':
        n_path = os.path.join(self.path, other)
        return n_path

    @keep_type()
    def join_ext(self, ext) -> '_BasePath':
        if ext is None:
            return self
        if not isinstance(ext, str):
            err_msg = "argument 'ext' should be a path or str object, not '{}'".format(type(ext))
            logger.error(err_msg)
            raise TypeError(err_msg)
        if not ext.startswith(self._FILE_EXT_CLS.EXT_SEP):
            ext = self._FILE_EXT_CLS.EXT_SEP + ext
        return self.path + ext

    @keep_type()
    def replace_ext(self, ext) -> '_BasePath':
        return self.radix.join_ext(ext)

    @keep_type()
    def __add__(self, other) -> '_BasePath':
        if isinstance(other, _BasePath):
            return self.join_path(other)
        elif isinstance(other, self._FILE_EXT_CLS):
            return self.join_ext(other)
        else:
            return self._data + other

    @keep_type()
    def copy(self) -> '_BasePath':
        return copy(self)

    @keep_type()
    def deepcopy(self) -> '_BasePath':
        return deepcopy(self)

    def makedir(self, mode=0o777, exist_ok=False):
        os.makedirs(self, mode=mode, exist_ok=exist_ok)


class PathCollection(_CollectionCustomStr, metaclass=LockChangeAttr):
    """Collection of Path objects, inherited from list built-in type"""
    _STR_CLS = None  # Path object must be initialized prior this can be used.


class Path(_BasePath):
    """Class defining a path, inherited from str built-in type.
    If an iterable is passed, return a PathCollection of multiple Path objects.

    >>> p = Path('a/b/c.d')
    >>> p
    Path: a/b/c.d
    >>> Path(None)
    Path: None
    >>> p.filename
    Path: c.d
    >>> p.isdir
    False
    >>> p.split_path
    [Path: a/b, Path: c.d]

    # Collections
    >>> p_c = Path(['a/b/c.d', 'e/f/g.h'])
    >>> p_c
    [Path: a/b/c.d, Path: e/f/g.h]
    >>> p_c.filename
    [Path: c.d, Path: g.h]
    >>> p_c.isdir
    [False, False]
    >>> p_c.split_path
    [[Path: a/b, Path: c.d], [Path: e/f, Path: g.h]]

    # As _MODIFY_COLLECTION_INPLACE is True, PathCollection object has the same behavior as Path:
    >>> PathCollection(['a/b/c.d']) == Path(['a/b/c.d'])
    True
    >>> PathCollection(['a/b/c.d'])
    [Path: a/b/c.d]

    # Types of supported iterables: list, tuple, set and inherited objects.
    >>> Path(['a/b/c.d', ['e/f/g.h'], ('i/j/k.l',), {'m/n/o.p'}])
    [Path: a/b/c.d, [Path: e/f/g.h], [Path: i/j/k.l], [Path: m/n/o.p]]
    """
    _COLLECTION_CLS = PathCollection
    _ALLOW_MULTIPLE = True  # Allow collections of objects: mandatory for filedialog.askopenfilenames
    _MODIFY_COLLECTION_INPLACE = True  # Make PathCollection._STR_CLS be Path


# Modification of PathCollection inplace:
Path([])


# Testing purposes
if __name__ == "__main__":
    m_path = Path(os.getcwd())
    import pdb

    pdb.set_trace()
