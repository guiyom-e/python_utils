# -*- coding: utf-8 -*-
"""
Main tools
"""
import sys
import os
import logging
import pdb
from collections import OrderedDict
from tkinter import ttk

from tools.logger import logger, change_logger_level
from tools import __help__

# Manage command line arguments
user_args = sys.argv[1:]
if '--debug' in user_args:
    change_logger_level(logging.DEBUG, logger=logger)
    DEBUG_MODE = True
    logger.info("Debug mode activated!")
else:
    change_logger_level(logging.INFO, logger=logger)
    DEBUG_MODE = False

# Other imports


TITLE = "Main window"

logger.debug('Imports OK.')
logger.info("Working directory: {}".format(os.getcwd()))


def reload_all_modules():
    from tools.helpers.utils import reload_modules
    reload_modules([], reload_func=True, ls_func_names='FUNCTIONS')


def reload_main(win, debug_mode=DEBUG_MODE, reload_modules=True):
    if win.on_closing():
        if reload_modules:
            reload_all_modules()
        main(debug_mode=debug_mode)
        win.quit()


def change_logger_to_info(root):
    change_logger_level(logging.INFO, logger)
    root.logger_frame.logging_handler.setLevel(logging.INFO)


def change_logger_to_debug(root):
    change_logger_level(logging.DEBUG, logger)
    root.logger_frame.logging_handler.setLevel(logging.DEBUG)


def debugger():
    try:
        logger.debug("Starting Python debugger...")
        pdb.set_trace()
    except Exception as err:
        logger.exception(err)


def main(debug_mode=DEBUG_MODE):
    # Imports are at this level, in case modules are reloaded.
    from tools.helpers.interface import MainTk
    # import functions here:
    from scripts import FUNCTIONS
    # import debug functions here:
    DEBUG_FUNCTIONS = []
    parts = OrderedDict([("sample functions", FUNCTIONS),
                        ])  # add functions here
    if debug_mode:
        parts['Debugging (developer only)'] = DEBUG_FUNCTIONS  # add debug functions here
    logger_level = logging.DEBUG if debug_mode else logging.INFO
    root = MainTk(parts, logger_level, help_msg=__help__, title=TITLE)
    if debug_mode:
        reload_but = ttk.Button(master=root.info_frame, text="Reload interface and scripts",
                                command=lambda: reload_main(root, debug_mode=debug_mode))
        reload_but.grid(row=2, column=2, sticky='se')
        ttk.Button(master=root.info_frame, text="logger INFO",
                   command=lambda: change_logger_to_info(root)).grid(row=2, column=0, sticky='e')
        ttk.Button(master=root.info_frame, text="logger DEBUG",
                   command=lambda: change_logger_to_debug(root)).grid(row=2, column=1, sticky='e')
        ttk.Button(master=root.info_frame, text="Standard mode",
                   command=lambda: reload_main(root, debug_mode=False)).grid(row=3, column=0, sticky='w')
        ttk.Button(master=root.info_frame, text="Open debugger",
                   command=debugger).grid(row=3, column=1, sticky='w')
        change_logger_to_debug(root)
    else:
        ttk.Button(master=root.info_frame, text="Advanced mode",
                   command=lambda: reload_main(root, debug_mode=True)).grid(row=3, column=0, sticky='w')
        change_logger_to_info(root)
    root.mainloop()
    logger.debug('Main window closed.')


if __name__ == '__main__':
    logger.info('Start of the program.')
    main()
    logger.info('End of the program.')
