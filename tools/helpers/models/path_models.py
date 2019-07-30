# -*- coding: utf-8 -*-
# open source project
"""
Classes to manipulate paths.
Path and PathCollection define custom strings/collections with pathname manipulations methods.
FileExt describes a file extension.
DefaultFiletypesDict defines a dictionary-like class with file types understandable by tkinter file dialogs.
"""
import os
from typing import Tuple
from copy import copy, deepcopy

from tools.helpers.models.str_models import _CustomStr, _CollectionCustomStr, _DynamicCustomStr
from tools.logger import logger

from tools.helpers.models.metaclasses import LockChangeAttr
from tools.helpers.models.types_models import keep_type


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

if PathCollection._STR_CLS is not Path:
    raise TypeError("PathCollection was not initialized correctly!")

# Testing purposes
if __name__ == "__main__":
    pass