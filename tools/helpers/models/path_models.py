# open source
import os
from typing import Tuple
from copy import copy, deepcopy

from tools.logger import logger
from tools.helpers.utils import isiterable


class _CustomStr(str):
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
    def format(self, *args, **kwargs):
        return self.__class__(super().format(*args, **kwargs))

    def upper(self, *args, **kwargs):
        return self.__class__(super().upper(*args, **kwargs))

    def lower(self, *args, **kwargs):
        return self.__class__(super().lower(*args, **kwargs))

    def swapcase(self, *args, **kwargs):
        return self.__class__(super().swapcase(*args, **kwargs))

    def join(self, *args, **kwargs):
        return self.__class__(super().join(*args, **kwargs))

    def title(self, *args, **kwargs):
        return self.__class__(super().title(*args, **kwargs))

    def capitalize(self, *args, **kwargs):
        return self.__class__(super().capitalize(*args, **kwargs))

    def strip(self, *args, **kwargs):
        return self.__class__(super().strip(*args, **kwargs))

    def lstrip(self, *args, **kwargs):
        return self.__class__(super().lstrip(*args, **kwargs))

    def rstrip(self, *args, **kwargs):
        return self.__class__(super().rstrip(*args, **kwargs))

    def replace(self, *args, **kwargs):
        return self.__class__(super().replace(*args, **kwargs))
    # TODO: add more methods


class _CollectionCustomStr(list):  # Collection (list) of _CustomStr objects (1 dimension only)
    _STR_CLS = _CustomStr

    def __str__(self):
        return str([str(ele) for ele in self])

    def __getattr__(self, item):
        if item in dir(self):
            print('already in dir')
            return self.__getattribute__(item)
        if item in dir(self._STR_CLS):  # Beta version
            if '__call__' not in dir(getattr(self._STR_CLS, item)):  # attribute or property
                return self.__class__([getattr(ele, item) for ele in self])

            def method(*args, **kwargs):  # method
                res = self.__class__([getattr(ele, item)(*args, **kwargs) for ele in self])
                return res

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

    def append(self, obj) -> None:
        obj = self._STR_CLS(obj)
        super().append(obj)

    def extend(self, iterable) -> None:
        iterable = [self._STR_CLS(ele) for ele in iterable]
        super().extend(iterable)

    def insert(self, index: int, obj) -> None:
        obj = self._STR_CLS(obj)
        super().insert(index, obj)


class _DynamicCustomStr(_CustomStr):  # Allow iterable
    _COLLECTION_CLS = _CollectionCustomStr
    _ALLOW_MULTIPLE = True  # Allow collections of objects. Priority over _ALLOW_CASTING

    def __new__(cls, *args, **kwargs):
        if (len(args) > 1) or (len(kwargs) > 1) or (args and kwargs):
            raise TypeError("'{}'() takes 1 positional argument but {} were given"
                            .format(cls.__name__, len(args) + len(kwargs)))
        data = args[0] if args else kwargs.popitem()[1] if kwargs else None
        data = cls._check_input(data)
        if isiterable(data):  # create a collection of _CustomStr
            ls = cls._COLLECTION_CLS()
            for sub_data in data:
                ls.append(cls.__new__(cls, sub_data))
            return ls
        return _CustomStr.__new__(cls, data)


class FileExt(_CustomStr):  # not dynamic
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
    _ALLOW_MULTIPLE = False  # Allow collections of objects: mandatory for filedialog.askopenfilenames
    _ALLOW_CASTING = False  # Allow non-string objects to be casted.
    _FILE_EXT_CLS = FileExt

    # Path properties
    @property
    def path(self) -> str:
        return self._data or ''

    @property
    def abspath(self) -> '_BasePath':
        return __class__(os.path.abspath(self.path))

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

    @property
    def split_path(self) -> Tuple['_BasePath', '_BasePath']:
        dirname, filename = os.path.split(self.path)
        return __class__(dirname), __class__(filename)

    @property
    def splitext(self) -> Tuple['_BasePath', _FILE_EXT_CLS]:
        radix, ext = os.path.splitext(self.path)
        return self.__class__(radix), self._FILE_EXT_CLS(ext)

    @property
    def dirname(self) -> '_BasePath':
        return self.__class__(os.path.dirname(self.path))
        # return self.split_path[0]  # should be equivalent

    @property
    def filename(self) -> '_BasePath':
        return self.split_path[1]

    @property
    def ext(self) -> _FILE_EXT_CLS:
        return self.splitext[1]

    @property
    def extension(self) -> _FILE_EXT_CLS:
        return self.ext

    @property
    def radix(self) -> '_BasePath':
        return self.splitext[0]

    @property
    def basis(self) -> '_BasePath':
        return self.radix

    @property
    def filename_radix(self) -> '_BasePath':
        return self.filename.radix

    @property
    def filename_basis(self) -> '_BasePath':
        return self.filename_radix

    @property
    def parent_dirname(self) -> '_BasePath':
        return self.dirname.dirname

    @property
    def short_dirname(self) -> '_BasePath':
        return self.dirname.split_path[-1]

    def join_path(self, other) -> '_BasePath':
        n_path = os.path.join(self.path, other)
        return self.__class__(n_path)

    def join_ext(self, ext) -> '_BasePath':
        if ext is None:
            return self
        if not isinstance(ext, str):
            err_msg = "argument 'ext' should be a path or str object, not '{}'".format(type(ext))
            logger.error(err_msg)
            raise TypeError(err_msg)
        if not ext.startswith(self._FILE_EXT_CLS.EXT_SEP):
            ext = self._FILE_EXT_CLS.EXT_SEP + ext
        return self.__class__(self._data + ext)

    def replace_ext(self, ext) -> '_BasePath':
        return self.radix.join_ext(ext)

    def __add__(self, other) -> '_BasePath':
        if isinstance(other, _BasePath):
            return self.join_path(other)
        elif isinstance(other, self._FILE_EXT_CLS):
            return self.join_ext(other)
        else:
            return self.__class__(self._data + other)

    def copy(self) -> '_BasePath':
        return copy(self)

    def deepcopy(self) -> '_BasePath':
        return deepcopy(self)

    def makedir(self, mode=0o777, exist_ok=False):
        os.makedirs(self, mode=mode, exist_ok=exist_ok)


class PathCollection(_CollectionCustomStr):
    _STR_CLS = _BasePath

    @property
    def filenames(self):
        return self.filename()
        # return PathCollection([ele.filename for ele in self])


class Path(_BasePath):
    _COLLECTION_CLS = PathCollection
    _ALLOW_MULTIPLE = True  # Allow collections of objects: mandatory for filedialog.askopenfilenames


# Testing purposes
if __name__ == "__main__":
    m_path = Path(os.getcwd())
    import pdb

    pdb.set_trace()
