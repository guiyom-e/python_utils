# -*- coding: utf-8 -*-
#  open source 2020
from abc import ABC
import psycopg2

from tools.helpers.db_managers.abstract_db_manager import AbstractDBManager


class PostgreSQLManager(AbstractDBManager):
    """PostreSQL Database manager"""
    _database_errors = psycopg2.Error

    def connect(self):
        """Connect to database"""
        self._connection = psycopg2.connect(**self._db_config)
