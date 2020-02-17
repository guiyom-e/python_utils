"""
server with socket
"""
import socket  # for socket
from threading import Thread
from time import sleep
from typing import Union

import numpy as np

from tools.logger import logger
from tools.helpers.servers.sockets.config_connection import CONFIG
from tools.helpers.servers.sockets.data_types import DataType


# TODO: make it work!
# TODO factorize code

class Server(Thread):
    """Server class

    >>> server = Server()
    >>> server.start()

    """

    def __init__(self, config: dict = None):
        super().__init__()
        # noinspection PyTypeChecker
        self._sock: socket.socket = None
        self._config = config or CONFIG
        self._is_active = True
        self._clients = []

    @property
    def host(self):
        return self._config.get("host", None)

    @property
    def port(self):
        return self._config.get("port", None)

    @property
    def auto_reload(self):
        return self._config.get("auto_reload", 0)

    def _connect(self):
        try:
            self._sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self._sock.bind((self.host, self.port))
        except socket.error as err:
            logger.error(f"Failed to use this address: {self.host}:{self.port}")
            logger.exception(err)
            return False
        logger.info(f"Server successfully set up at {self.host}:{self.port}")
        return True

    def run(self):
        is_connected = self._connect()
        if not is_connected:  # todo: handle error
            return False
        self._sock.listen(2)
        logger.info("Server waiting for a connection...")

        while self._is_active:
            try:
                connection, _client = self._sock.accept()
                self._clients.append(connection)

                # TODO: do something

            except (OSError, IOError) as err:
                logger.error(f"Server error: {err}")
                logger.exception(err)
        logger.info("Server closing...")
        self._clients = []
        return True

    def stop(self):
        self._is_active = False
        if self._sock:
            self._sock.close()

    def send(self, *args: Union[str, int]):
        package = bytes()
        for arg in args:
            if isinstance(arg, (int, np.integer)):
                package += int(arg).to_bytes(1, "big", signed=False)
            else:
                package += arg.encode(encoding="ascii")
        self._sock.send(package)

    @staticmethod
    def decode(input_bytes: bytes, expected_type: DataType):
        if expected_type is DataType.STR:
            decoded_str = input_bytes.decode(encoding="ascii")
        elif expected_type == DataType.INT:
            decoded_str = int.from_bytes(input_bytes, "little")
        else:
            raise TypeError(f"Invalid type expected: {expected_type}")
        return decoded_str

    def receive(self, nb_bytes: int = 3, expected_type: DataType = DataType.STR):
        message = bytes()
        while len(message) < nb_bytes:
            message += self._sock.recv(nb_bytes - len(message))
        decoded_command = self.decode(message, expected_type)
        logger.debug(f"Received command: {decoded_command}")
        return decoded_command
