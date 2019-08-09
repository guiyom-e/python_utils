# -*- coding: utf-8 -*-
# open source project
"""
Add advanced dialogs in the wrapped messagebox, simpledialog and filedialog module-like objects.
Import messagebox, simpledialog and filedialog from this file instead from tkinter to benefit from enhanced modules.
"""
from tools.helpers.interface.wrappers import (_messagebox, _MessageBox,
                                              _simpledialog, _SimpleDialog,
                                              _filedialog, _FileDialog)

# Import custom dialogs
from tools.helpers.interface.custom_messagebox import ask_custom_question
from tools.helpers.interface.custom_dialog import (ask_multiple_questions, ask_option, ask_checkbox,
                                                   ask_radio_button)
from tools.helpers.interface.text_frame import showtext
from tools.helpers.interface.date_picker import askdate, askperiod


class _AdvancedMessageBox(_MessageBox):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to messagebox"""
    _base_module = _messagebox
    # For signature in IDE
    showtext = showtext
    askcustomquestion = ask_custom_question

    _custom_func = {'showtext': showtext,
                    'askcustomquestion': askcustomquestion,
                    }


class _AdvancedSimpleDialog(_SimpleDialog):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to simpledialog"""
    _base_module = _simpledialog
    # For signature in IDE
    askoption = ask_option
    askcheckbox = ask_checkbox
    askradiobutton = ask_radio_button
    ask_multiple_questions = ask_multiple_questions
    askdate = askdate
    askperiod = askperiod

    _custom_func = {'askoption': askoption,
                    'askcheckbox': askcheckbox,
                    'askradiobutton': askradiobutton,

                    'askdate': askdate,
                    'askperiod': askperiod,

                    'ask_multiple_questions': ask_multiple_questions,
                    }


class _AdvancedFileDialog(_FileDialog):  # inheritance is just for IDE to show attributes
    """Add custom dialogs to simpledialog"""
    _base_module = _filedialog


messagebox = _AdvancedMessageBox()  # WARN: tkinter messagebox modified
simpledialog = _AdvancedSimpleDialog()  # WARN: tkinter simpledialog modified
filedialog = _AdvancedFileDialog()  # WARN: tkinter filedialog modified

if __name__ == '__main__':
    import datetime

    print(messagebox.askokcancel(message='OK?'))  # based on tkinter messagebox
    print(messagebox.showtext(text="Hello!"))
    print(messagebox.askcustomquestion(choices=[1, 2]))

    print(simpledialog.askinteger(title='title', prompt='Integer?'))  # based on tkinter simpledialog
    print(simpledialog.askdate(title='title'))
    print(simpledialog.askperiod(choices=[4, datetime.datetime(2019, 8, 5), datetime.datetime.now()]))
    print(simpledialog.askoption(choices=[4, 5]))
    print(simpledialog.askcheckbox(choices=[4, 5]))
    print(simpledialog.askradiobutton(choices=[4, 5]))
    print(simpledialog.ask_multiple_questions(choices=[[1, 2]]))
