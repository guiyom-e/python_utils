# -*- coding: utf-8 -*-
# open source project
"""
Various model classes and functions linked to them.
"""
import functools


class Reference:
    """Reference class"""
    pass


class Wildcard:
    """Class to define wildcard objects"""
    def __repr__(self):
        return "<Wildcard object>"


class Property(object):
    """Emulate PyProperty_Type() in Objects/descrobject.c"""

    def __init__(self, fget=None, fset=None, fdel=None, doc=None):
        self.fget = fget
        self.fset = fset
        self.fdel = fdel
        if doc is None and fget is not None:
            doc = fget.__doc__
        self.__doc__ = doc

    def __get__(self, obj, objtype=None):
        if obj is None:
            return self
        if self.fget is None:
            raise AttributeError("unreadable attribute")
        return self.fget(obj)

    def __set__(self, obj, value):
        if self.fset is None:
            raise AttributeError("can't set attribute")
        self.fset(obj, value)

    def __delete__(self, obj):
        if self.fdel is None:
            raise AttributeError("can't delete attribute")
        self.fdel(obj)

    def getter(self, fget):
        return type(self)(fget, self.fset, self.fdel, self.__doc__)

    def setter(self, fset):
        return type(self)(self.fget, fset, self.fdel, self.__doc__)

    def deleter(self, fdel):
        return type(self)(self.fget, self.fset, fdel, self.__doc__)


def add_tag(tag='tag', tag_value=True):
    """Set an attribute to a function or a property."""

    def decorator(func):
        if type(func) is property:
            wrapper = Property(func.fget, func.fset, func.fdel, func.__doc__)  # property-like object
            wrapper.__setattr__(tag, tag_value)
            return wrapper

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        setattr(wrapper, tag, tag_value)
        return wrapper

    return decorator


def keep_type(func_type='function'):
    """Set the attribute 'keep_type' to a method or property and convert its result to original class.

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


if __name__ == '__main__':
    # Test keep_type decorator
    class TestKeepType:
        def __init__(self, *args):
            self.disp = args[0] if args else 1
            print('init: {}'.format(args))
            super().__init__()

        def __repr__(self): return super().__repr__() + " - {}".format(self.disp)

        # Property: two options
        @keep_type()
        @property
        def a1(self): return 3

        @keep_type(property)
        def a2(self): return 4

        # method
        @keep_type()
        def b(self): return 5

        # classmethod
        # The following scheme is not possible...
        @classmethod
        @keep_type()
        def c1(cls): return 6

        # ...but this scheme works!
        @keep_type('classmethod')  # both classmethod and 'classmethod' are allowed
        def c2(cls): return 7

        # staticmethod
        # can not work since the class is needed to return an instance of class
        @staticmethod
        @keep_type
        def d(): return 8

    test_kt = TestKeepType(2)
    print([test_kt.a1, test_kt.a2, test_kt.b(), TestKeepType.c2()])  # ok
    print(TestKeepType.c1())  # does not return what is expected
    # print(test_kt.d())  # raises an error
