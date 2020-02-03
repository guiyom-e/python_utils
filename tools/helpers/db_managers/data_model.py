# -*- coding: utf-8 -*-
#  open source 2020

from abc import ABC
from enum import Enum


class DataModel(ABC):
    """Base model for data structures which aim is to be added to a database

    Data attributes can be:
    - numbers (int, float)
    - strings
    - None
    - other DataModel objects
    - other objects with a __str__ function used to store the object to database
    """
    _custom_mapping_attr_to_bdd_col = {}
    _custom_table_name = ""
    _custom_name = ""
    _custom_id_name = ""

    def __init__(self):
        self._db_key = None

    def save_db_key(self, foreign_key: int):
        self._db_key = foreign_key

    @property
    def is_already_saved_to_db(self):
        if self._db_key is None:
            return False
        return True

    @property
    def db_key(self):
        return self._db_key

    @property
    def mapping_attr_to_database_col(self):
        """Conversion dict between Python data attributes and BDD column names"""
        return self._custom_mapping_attr_to_bdd_col or {ele: ele.capitalize() for ele in self.get_data_attr()}

    @property
    def table_name(self):
        """Associated table name. By default: '[class name]s'"""
        return self._custom_table_name or self.__class__.__name__ + "s"

    @property
    def name(self):
        return self._custom_name or self.__class__.__name__

    @property
    def id_name(self):
        return self._custom_id_name or self.name + "Id"

    def __repr__(self):
        res = "{}\n".format(self.__class__.__name__)
        for attr in self.get_data_attr():
            res += "{}: {}\n".format(attr, getattr(self, attr))
        return res

    def get_data_attr(self):
        """Get data attributes, i.e public attributes that are not defined in the class
        (i.e. no method nor class attribute).

        WARNING: it is assumed __class__ attribute is not overridden
        """
        return [ele for ele in set(dir(self)) - set(dir(self.__class__)) if not ele.startswith("_")]

    def get_data_attr_with_simple_type(self):
        """Get data attributes that are of simple type, i.e. not deriving from BaseModel.

        WARNING: this method access all attributes with getattr, so some code can be executed (e.g. in properties)
        """
        return [ele for ele in self.get_data_attr() if not isinstance(getattr(self, ele), DataModel)]

    def get_data_attr_with_data_models(self):
        return [ele for ele in self.get_data_attr() if isinstance(getattr(self, ele), DataModel)]

    def __hash__(self):
        return hash("-".join([str(ele) for ele in self.get_data_attr()]))

    def __setattr__(self, key, value):
        if key in self.get_data_attr():
            raise AttributeError("DataModel objects are not mutable!")
        else:
            super().__setattr__(key, value)


class NameAsStrEnum(Enum):
    """Enum with __str__ method overridden to return enum name (ex: str(EnumClass.INSTANCE) returns INSTANCE)"""

    def __str__(self):
        return self.name
