# -*- coding: utf-8 -*-
# open source project
import logging
import os

from tools import __id_filename__

DEFAULT_CONSOLE_LEVEL = logging.INFO


def _set_default_dir(id_filename):
    """Try to set working directory to 'tools' directory parent.

    :return tuple (error, message). error is None in case of success, else Exception"""
    res, msg = None, ""
    try:
        _curr_dir = os.getcwd()
        msg = "Current working directory: {}".format(_curr_dir)
        _tools_dir = os.path.join(_curr_dir, 'tools')
        # if current directory is already python_tools
        if os.path.isdir(_tools_dir) and id_filename in os.listdir(_tools_dir):
            return None, msg
        # if current directory is tools or its subdirectories
        elif id_filename in os.listdir(_curr_dir):
            os.chdir("..")
        elif id_filename in os.listdir(os.path.dirname(_curr_dir)):
            os.chdir("../..")
        elif id_filename in os.listdir(os.path.dirname(os.path.dirname(_curr_dir))):
            os.chdir("../../..")
        # if current directory is a subdirectory of python_tools
        elif os.path.isdir(os.path.join(os.path.dirname(_curr_dir), 'tools')) \
                and id_filename in os.listdir(os.path.join(os.path.dirname(_curr_dir), 'tools')):
            os.chdir("..")
        elif os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(_curr_dir)), 'tools')) \
                and id_filename in os.listdir(os.path.join(os.path.dirname(os.path.dirname(_curr_dir)), 'tools')):
            os.chdir("../..")
        elif os.path.isdir(os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_curr_dir))), 'tools')) \
                and id_filename in os.listdir(
            os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(_curr_dir))),
                         'tools')):
            os.chdir("../../..")
        else:
            err_msg = "Failed to set default working directory automatically!"
            res = (ValueError(err_msg), ";".join([msg, err_msg]))
    except FileNotFoundError as err:
        res = (err, "Failed to set default working directory automatically! (FileNotFoundError)")
    except PermissionError as err:
        res = (err, "Failed to set default working directory automatically! (PermissionError)")
    if not res:
        res = (None, msg + "; New working directory: {}".format(os.getcwd()))
    return res


def _initialize_logger(output_dir):
    _logger = logging.getLogger()
    _logger.setLevel(logging.DEBUG)

    # create console handler and set level to info
    handler = logging.StreamHandler()
    handler.setLevel(DEFAULT_CONSOLE_LEVEL)
    formatter = logging.Formatter("%(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # create error file handler and set level to error
    handler = logging.FileHandler(os.path.join(output_dir, "error.log"), "w", encoding=None, delay="true")
    handler.setLevel(logging.ERROR)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)

    # create debug file handler and set level to debug
    handler = logging.FileHandler(os.path.join(output_dir, "debug.log"), "w")
    handler.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(module)s %(funcName)s %(lineno)d - %(message)s")
    handler.setFormatter(formatter)
    _logger.addHandler(handler)
    return _logger


_err, _msg = _set_default_dir(__id_filename__)
_log_path = os.path.join(os.getcwd(), 'tools/logs/')
os.makedirs(_log_path, exist_ok=True)

logger = _initialize_logger(_log_path)
if _err:
    logger.exception(_err)
    logger.error(_msg)
else:
    logger.debug(_msg)
logger.debug("Logger loaded successfully. Logging directory: {}".format(_log_path))


def change_logger_level(level=logging.INFO, logger=logger, handler_index=0):
    conv_lvl = {"debug": logging.DEBUG, "info": logging.INFO,
                "warning": logging.WARNING, "warn": logging.WARN,
                "error": logging.ERROR, "critical": logging.CRITICAL}
    if isinstance(level, str):
        level = level.lower()
        level = conv_lvl.get(level, logging.INFO)
    logger.handlers[handler_index].setLevel(level)
    logger.debug("Logger level has been changed to '{}' (handler n°{}).".format(level, handler_index))
    return logger


# For testing purposes.
if __name__ == '__main__':
    logger.debug("Debug message.")
    logger.info("Info message.")
    logger.warning("Warning message.")
    logger.error("Error message.")
    logger.exception(TypeError("Test exception."))
