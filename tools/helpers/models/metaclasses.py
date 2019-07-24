# open source
class Singleton(type):
    """Metaclass that authorize only one instance of a class."""
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class LockChangeAttr(type):
    """Metaclass that locks attribute modification after a certain limit"""
    _modification_count = {}
    _modification_limit = 2
    _attr_exceptions = []

    def __setattr__(cls, key, value):
        if key not in cls._modification_count:
            cls._modification_count[key] = 0
        cls._modification_count[key] += 1
        if cls._modification_count[key] > cls._modification_limit and key not in cls._attr_exceptions:
            print("Warn: modification of attribute '{}' has raised its limit ({})".format(key, cls._modification_limit))
            return
        return super(LockChangeAttr, cls).__setattr__(key, value)
