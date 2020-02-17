# -*- coding: utf-8 -*-
#  open source 2020
import enum
import functools
from abc import ABC, abstractmethod
from typing import Tuple, List, Type, Union, Optional, Dict, Any

from tools.helpers.db_managers.data_model import DataModel
from tools.helpers.db_managers.db_data_types import DataTypes
from tools.logger import logger


def handle_db_errors(errors_to_catch: List[Type[Exception]], error_msg=""):
    """Decorator to catch database exceptions in a method"""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(self, *args, **kwargs):
            try:
                result = func(self, *args, **kwargs)
            except errors_to_catch as err:
                err_msg = error_msg + "\n" if error_msg else ""
                logger.debug(err_msg + f"Error in method {func.__name__}: {err}")
                logger.exception(err)
                self.reset_connection()
                return None
            return result

        return wrapper

    return decorator


class AbstractDBManager(ABC):
    """Database manager to save postings to database"""
    _database_errors = ()

    def __init__(self, db_config: dict):
        """Init method

        :param db_config: dictionary with these possible keys (cf. specific doc for each database):
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

    @abstractmethod
    def connect(self) -> None:
        """Connect to database"""
        self._connection = None

    def reset_cursor(self) -> None:
        """Reset cursor"""
        self._cursor_var = None

    def reset_connection(self) -> None:
        """Reset connection to database"""
        self._connection.reset()
        self.reset_cursor()

    def disconnect(self) -> None:
        """Close the connection to database"""
        self._cursor_var = None
        self._connection.close()

    @property
    def _cursor(self) -> Optional[Any]:
        if self._connection is None:
            logger.error("Can not get a cursor as the connection is None! Returning None.")
            return None
        if self._cursor_var is None:
            self._cursor_var = self._connection.cursor()
        return self._cursor_var

    @staticmethod
    def _obj_to_db_str(obj: object, ids: dict = None) -> Any:
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
        :return: SQL query
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

    def _save_data_object_to_db(self, obj: DataModel, ids: dict = None) -> Tuple[int, Dict[str, int]]:
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
        except self._database_errors as err:
            raise err  # error is caught after
        data_id = self._cursor.fetchone()[0]
        ids.update({obj.id_name: data_id})
        return data_id, ids

    @handle_db_errors(_database_errors, "Error to save DataModel object:")
    def save_data_object_to_db(self, obj: DataModel, saved_ids: dict) -> Union[True, None]:
        """Save a DataModel object to database

        :param obj: DataModel object to save
        :param saved_ids: Ids of lines saved to db are saved in this dictionary inplace
        :return None if a database exception is raised, else True
        """
        _obj_id, db_ids = self._save_data_object_to_db(obj)
        saved_ids.update(db_ids)
        return True

    @handle_db_errors(_database_errors, "Error while committing changes:")
    def commit(self) -> Union[True, None]:
        """Commit to database"""
        self._connection.commit()
        self.reset_cursor()
        return True

    @handle_db_errors(_database_errors, "Error in query:")
    def execute(self, *query) -> Union[True, None]:
        """Execute a query"""
        self._cursor.execute(*query)
        return True

    @handle_db_errors(_database_errors)
    def fetchone(self) -> Optional[tuple]:
        """Same as cursor.fetchone()"""
        return self._cursor.fetchone()

    @handle_db_errors(_database_errors)
    def fetchall(self) -> Optional[List[tuple]]:
        """Same as cursor.fetchall()"""
        return self._cursor.fetchall()

    @handle_db_errors(_database_errors, "Error while creating table:")
    def create_table(self, table: str, fields: List[Tuple[str, DataTypes]]) -> Union[True, None]:
        """Create a table

        :param table: table name
        :param fields: list of fields with their type [(field_name, field_type), ...]
        :return None if a database exception is raised, else True
        """
        pass
        raise NotImplementedError

    def delete_table(self, table, where_column=None, where_value=None) -> Union[True, None]:
        """Delete a table or a selected row

        :param table: name of the table to delete
        :param where_column: if None, the entire table is deleted, else delete the rows with column_value in column_name
        :param where_value: value of the where_column in the rows to delete. If None, all rows are deleted
        (no row field can be equal to None/NULL)
        :return True if the deletion has been successfully committed, else False
        """
        if where_column is None:
            # noinspection SqlWithoutWhere,SqlResolve
            query = f"""DELETE FROM "{table}" """
        else:
            # noinspection SqlResolve
            query = f"""DELETE FROM "{table}" WHERE "{where_column}" = {where_value}"""
        logger.debug("Query generated: {}".format(query))
        if self.execute(query):
            return self.commit()
        return None

    @handle_db_errors(_database_errors, "Error in insertion query:")
    def insert_rows(self, table: str, values_dict: Dict[str, Any]) -> Union[True, None]:
        query = None
        raise NotImplementedError

    @handle_db_errors(_database_errors, "Error in selection query:")
    def select_rows(self, table: str, fields_selected: List[str],
                    where_column=None, where_value=None) -> Optional[List[tuple]]:
        fields_selected = '"{}"'.format('", "'.join(fields_selected)) if fields_selected else "*"
        if where_column is None:
            # noinspection SqlWithoutWhere,SqlResolve
            query = f"""SELECT {fields_selected} FROM "{table}" """
        else:
            # noinspection SqlResolve
            query = f"""SELECT {fields_selected} FROM "{table}" WHERE "{where_column}" = {where_value}"""
        logger.debug("Query generated: {}".format(query))
        if self.execute(query):
            return self.fetchall()
        return None

    @handle_db_errors(_database_errors, "Error in update query:")
    def update_rows(self, table: str, set_column: str, set_value: Any,
                    where_column: str = None, where_value: Any = None) -> Union[True, None]:
        query_str = f'''UPDATE %s SET %s = %s WHERE %s = %s;'''
        query = (query_str, (table, set_column, set_value, where_column, where_value))
        if self.execute(query):
            return self.commit()
        return None
