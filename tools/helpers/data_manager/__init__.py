# -*- coding: utf-8 -*-
# open source project
"""
Data manager

Provides high level function to check paths, open and read data files

- file_utils: various functions
- filepath_manager: functions to check paths, using file dialogs
- data_loader: functions to open files: CSV or Excel
- date_writer: functions to write files: Excel or PowerPoint
- plots: functions to create simple plots

Imports:
logger, utils, models, interface
--------------------------------------------
    |                   |               |  |
    v                   v               v  v
 file_utils --> filepath_manager --> data_loader
                                 |-> data_writer
"""

from tools.helpers.data_manager.filepath_manager import open_file, save_file, open_dir  # Must be the first import
from tools.helpers.data_manager.data_loader import read_data_file
from tools.helpers.data_manager.data_writer import save_excel_file, export_img_to_powerpoint
from tools.helpers.data_manager.plots import save_plot, save_error_graph


__all__ = [
    'open_file',
    'open_dir',
    'save_file',

    'read_data_file',
    'save_excel_file',
    'export_img_to_powerpoint',

    'save_plot',
    'save_error_graph',
]

__version__ = '1.4.2'
