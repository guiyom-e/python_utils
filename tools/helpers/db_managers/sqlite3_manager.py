# -*- coding: utf-8 -*-
#  open source 2020
from abc import ABC
import sqlite3

from tools.helpers.db_managers.abstract_db_manager import AbstractDBManager


class Sqlite3Manager(AbstractDBManager):
    """SQLite3 Database manager"""
    _database_errors = sqlite3.Error

    def connect(self):
        """Connect to database"""
        self._connection = sqlite3.connect(**self._db_config)
