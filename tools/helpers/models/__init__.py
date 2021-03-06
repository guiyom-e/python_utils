# -*- coding: utf-8 -*-
# open source project
"""
Model classes
"""
from tools.helpers.models.metaclasses import Singleton
from tools.helpers.models.path_models import DefaultFiletypesDict, FileExt, Path, PathCollection
from tools.helpers.models.types_models import Reference, Wildcard, Property
from tools.helpers.models.dict_models import IdentityDict, BaseDict

__all__ = [
    'Singleton',  # metaclass

    'Path',
    'PathCollection',
    'DefaultFiletypesDict',
    'FileExt',

    'Reference',
    'Wildcard',
    'Property',

    'IdentityDict',
    'BaseDict',
]
