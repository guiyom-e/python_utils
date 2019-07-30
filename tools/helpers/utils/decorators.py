# -*- coding: utf-8 -*-
# open source project
"""
Wrappers for date functions
"""
import pandas as pd
import functools


def handle_datetime_serie(func):
    """Decorator to make functions converting dates usable for pandas Series or lists.

    Function requirements:
        - first argument must be a datetime-like object

    Performance warning: in many cases, the pandas Serie method "apply" is slower than direct/vectorial operations
                         Consider using the ".dt" accessor for example
    General warning: using complex objects with inheritances or __instancecheck__ method is not recommended
    """

    @functools.wraps(func)  # update the wrapper function to look like the wrapped function.
    def wrapper(obj, *args, **kwargs):
        if isinstance(obj, pd.Series):
            n_obj = pd.to_datetime(obj)
            return n_obj.apply(lambda x: func(x, *args, **kwargs))
        if isinstance(obj, list):
            return [func(ele, *args, **kwargs) for ele in obj]
        return func(obj, *args, **kwargs)

    return wrapper


def handle_datetime_dataframe(func):
    """Decorator to make functions converting dates usable for pandas DataFrame.

    Function requirements:
        - first argument can be a pandas Serie object
        - keyword argument 'inplace' may exist (used for DataFrame objects) but:
            * must not be passed as a positional argument
            * is False by default

    General warning: using complex objects with inheritances or __instancecheck__ method is not recommended
    """
    @functools.wraps(func)  # update the wrapper function to look like the wrapped function.
    def wrapper(obj, *args, **kwargs):
        if isinstance(obj, pd.DataFrame):
            inplace = kwargs.get('inplace', False)
            n_obj = obj if inplace else pd.DataFrame()
            for col in obj.columns:
                n_obj[col] = func(pd.to_datetime(obj[col]), *args, **kwargs)
            if inplace:
                return None
            return n_obj
        return func(obj, *args, **kwargs)

    return wrapper


def handle_datetime_pandas_objects(func):
    """Decorator to make functions converting dates usable for pandas Series and DataFrame.

    Function requirements:
        - first argument must be a datetime-like object
        - keyword argument 'inplace' may exist (used for DataFrame objects) but:
            * must not be passed as a positional argument
            * must not be used by the function itself

    Performance warning: in many cases, the pandas Serie method "apply" is slower than direct/vectorial operations
                         Consider using the ".dt" accessor for example
    General warning: using complex objects with inheritances or __instancecheck__ method is not recommended
    """
    wrapper = functools.update_wrapper(handle_datetime_dataframe(handle_datetime_serie(func)), func)
    return wrapper
