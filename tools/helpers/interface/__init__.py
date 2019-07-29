# open source
"""This module provides classes and functions based on tkinter module.

Files:
    - wrappers: enhances and replaces tkinter filedialog and messagebox modules
    - custom_messagebox: add a new method to messagebox to allow customized answers in a dialog window
    - date_picker: interface with a calendar to select a date
    - selector: interface to select an element inside a list
    - logger_widget: handler and frame to show logging outputs in tkinter windows
    - anomalies: show error messages on errors
    - main_interface: simple interface with multiple parts. Each button correspond to a script
"""
from tools.helpers.interface.basics import CustomTk, center   # Must be the first import

from tools.helpers.interface.date_picker import get_user_date
from tools.helpers.interface.custom_dialog import OptionMenuDialog, RadioSelectorDialog, CheckBoxSelectorDialog
from tools.helpers.interface.custom_messagebox import CustomQuestionDialog, CustomQuestionFrame
from tools.helpers.interface.text_frame import TextFrame
from tools.helpers.interface.anomalies import (raise_anomaly, raise_bad_extension_anomaly,
                                               raise_no_file_selected_anomaly)
from tools.helpers.interface.advanced_wrappers import messagebox, filedialog, simpledialog

from tools.helpers.interface.main_interface import MainTk
from tools.helpers.interface.tooltip import ToolTip
from tools.helpers.interface.logger_widget import LoggingHandlerFrame


__all__ = [
    'CustomTk',
    'center',

    'messagebox',
    'filedialog',
    'simpledialog',

    'get_user_date',

    'raise_anomaly',
    'raise_bad_extension_anomaly',
    'raise_no_file_selected_anomaly',

    'MainTk',

    'OptionMenuDialog',
    'RadioSelectorDialog',
    'CheckBoxSelectorDialog',
    'ToolTip',
    'TextFrame',
    'LoggingHandlerFrame',
    'CustomQuestionDialog',
    'CustomQuestionFrame',
]

__version__ = '2.0.0'
