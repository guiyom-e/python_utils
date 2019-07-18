# open source
from collections import UserDict


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
