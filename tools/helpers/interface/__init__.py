# -*- coding: utf-8 -*-
# open source project

"""This module provides classes and functions based on tkinter module.

Files:
    - basics: basic classes and functions
    - wrappers and advanced_wrappers: replace and enhance tkinter filedialog, simpledialog and messagebox modules
    - custom_messagebox: add a new method to messagebox to allow customized answers in a dialog window
    - custom_dialog: add new methods to simpledialog with check boxes, radio buttons, option menus or a mix.
    - date_picker: interface with a calendar to select a date
    - text_frame: display text in a frame
    - logger_widget: handler and frame to show logging outputs in tkinter windows
    - tooltip: easily add a tooltip on a widget
    - anomalies: show error messages on errors
    - main_interface: simple interface with multiple parts. Each button correspond to a function
"""
from tools.helpers.interface.basics import CustomTk, center   # Must be the first import

from tools.helpers.interface.date_picker import get_user_date, DatePickerFrame, DateSelectorFrame
from tools.helpers.interface.custom_dialog import OptionMenuFrame, RadioButtonFrame, CheckBoxFrame
from tools.helpers.interface.custom_messagebox import CustomQuestionFrame
from tools.helpers.interface.text_frame import TextFrame
from tools.helpers.interface.anomalies import (raise_anomaly, raise_bad_extension_anomaly,
                                               raise_no_file_selected_anomaly)
from tools.helpers.interface.advanced_wrappers import messagebox, filedialog, simpledialog

from tools.helpers.interface.tooltip import ToolTip
from tools.helpers.interface.logger_widget import LoggingHandlerFrame
from tools.helpers.interface.main_interface import MainTk


__all__ = [
    'CustomTk',
    'center',

    'get_user_date',  # deprecated
    'DatePickerFrame',
    'DateSelectorFrame',

    'OptionMenuFrame',
    'RadioButtonFrame',
    'CheckBoxFrame',

    'CustomQuestionFrame',

    'TextFrame',

    'raise_anomaly',
    'raise_bad_extension_anomaly',
    'raise_no_file_selected_anomaly',

    'messagebox',
    'filedialog',
    'simpledialog',

    'ToolTip',

    'LoggingHandlerFrame',

    'MainTk',
]

__version__ = '2.1.1'
