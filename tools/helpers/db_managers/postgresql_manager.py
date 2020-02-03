# -*- coding: utf-8 -*-
#  open source 2020
from abc import ABC
from typing import Tuple, List
import psycopg2

from tools.helpers.db_managers.data_model import DataModel
from tools.logger import logger


class PostgreSQLAbstractManager(ABC):
    """Database manager to save postings to database"""

    def __init__(self, db_config: dict):
        """Init method

        :param db_config: dictionary with these possible keys (cf. psycopg2.connect doc):
            - *dbname*: the database name
            - *database*: the database name (only as keyword argument)
            - *user*: user name used to authenticate
            - *password*: password used to authenticate
            - *host*: database host address (defaults to UNIX socket if not provided)
            - *port*: connection port number (defaults to 5432 if not provided)
        """
        self._db_config = db_config
        self._connection = None
        self._cursor_var = None

    def connect(self):
        """Connect to database"""
        self._connection = psycopg2.connect(**self._db_config)

    def reset_cursor(self):
        """Reset cursor"""
        self._cursor_var = None

    def reset_connection(self):
        """Reset connection to database"""
        self._connection.reset()
        self.reset_cursor()

    def disconnect(self):
        """Close the connection to database"""
        self._cursor_var = None
        self._connection.close()

    @property
    def _cursor(self):
        if self._connection is None:
            logger.error("Can not get a cursor as the connection is None! Returning None.")
            return None
        if self._cursor_var is None:
            self._cursor_var = self._connection.cursor()
        return self._cursor_var

    @staticmethod
    def _obj_to_db_str(obj: object, ids: dict = None):
        """Convert an object to a correct string for SQL"""
        if obj is None:
            return None
        elif isinstance(obj, DataModel) and ids:
            res = ids[obj.id_name]
        elif isinstance(obj, list):
            res = " ".join(obj)
        elif isinstance(obj, (float, int, bytes)):
            res = obj
        else:
            res = "{}".format(obj)
        return res or None  # returns a 'NULL' string if obj is empty

    def _generate_insertion_query(self, obj: DataModel, ids: dict = None) -> Tuple[str, List[str]]:
        """Generates an insertion SQL query to add a Python obj to a Postgres table.

        :param obj: Python object of type DataModel
        Default mapping is {ele: ele.capitalize() for ele in obj.get_data_attr_with_simple_type()}
        :return: PostgreSQL query
        """
        mapping = obj.mapping_attr_to_database_col  # mapping dict between attributes and column names
        table_name = obj.table_name
        col_str = ""
        values_str = []
        returning_id_str = obj.id_name
        for attr, col in mapping.items():
            value = getattr(obj, attr)

            # generate columns string
            if isinstance(value, DataModel):
                _new_col = '"{}"'.format(value.id_name)
            else:
                _new_col = '"{}"'.format(col)
            if col_str:
                col_str = ", ".join([col_str, _new_col])
            else:
                col_str = _new_col

            # generate values string
            values_str.append(self._obj_to_db_str(value, ids))

        query_str = 'INSERT INTO public."{table}" ({columns}) VALUES ({values}) RETURNING "{id_to_return}";'
        placeholder = ", ".join(["%s" for _ in values_str])  # use a placeholder to let psycopg2 format te string itself
        query_str = query_str.format(table=table_name, columns=col_str, values=placeholder,
                                     id_to_return=returning_id_str)
        query = (query_str, values_str)  # use this query format to avoid unescaped characters in values
        logger.debug("Query generated: {}".format(query))
        return query

    def _save_data_object_to_db(self, obj: DataModel, ids: dict = None):
        """Recursively add data objects to BDD. Returns id of the current object
        and dictionary of the previous data ids (set recursively)"""
        ids = ids or {}  # dictionary of data ids of type DataModel / foreign keys
        # recursively explore obj attributes that are also DataModel objects
        for attr in obj.get_data_attr_with_data_models():
            data_obj = getattr(obj, attr)
            # if the object already exists in the db, the foreign key (data_id) is used
            if data_obj.is_already_saved_to_db:
                data_id = data_obj.db_key
            else:  # else, the object is saved to the db and the foreign key is retrieved
                data_id, ids = self.save_data_object_to_db(data_obj, ids)
            ids.update({data_obj.id_name: data_id})
        query = self._generate_insertion_query(obj, ids)  # tuple
        try:
            self._cursor.execute(*query)
        except psycopg2.Error as err:
            raise err  # error is caught after
        data_id = self._cursor.fetchone()[0]
        ids.update({obj.id_name: data_id})
        return data_id, ids

    def save_data_object_to_db(self, obj: DataModel, saved_ids: dict):
        """Save a DataModel object to database

        :param obj: DataModel object to save
        :param saved_ids: Ids of lines saved to db are saved in this dictionary inplace
        :return False if a psycopg2.Error is raised, else True
        """
        try:
            _obj_id, db_ids = self._save_data_object_to_db(obj)
        except psycopg2.Error as err:
            logger.debug("Error to save DataModel object '{}':\n{}".format(obj, err))
            logger.exception(err)
            self.reset_connection()
            return False
        saved_ids.update(db_ids)
        return True

    def commit(self):
        """Commit to database"""
        try:
            self._connection.commit()
        except psycopg2.Error as err:
            logger.error("Error while committing changes:\n{}".format(err))
            logger.exception(err)
            self.reset_connection()
            return False
        self.reset_cursor()
        return True

    def execute(self, *query):
        """Execute a query"""
        try:
            self._cursor.execute(*query)
        except psycopg2.Error as err:
            logger.debug("Error in query '{}':\n{}".format(query, err))
            self.reset_connection()
            return False
        return True
