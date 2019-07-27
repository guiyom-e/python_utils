# open source
"""
Modified messagebox and filedialog (tkinter modules)
to avoid empty windows that cannot be closed before the end of the program.
"""
import tkinter as tk
from typing import List, Tuple
from tkinter import Tk, TclError
from tkinter import TclError
from tkinter import messagebox as msg_box
from tkinter import filedialog as f_dialog

# Import and rename
from tools.helpers.interface.custom_messagebox import ask_custom_question
from tools.helpers.interface.selector_messagebox import ask_multiple_questions, ask_option
from tools.helpers.interface.text_frame import showtext


def _wrapper(module, item, withdraw=True):
    """Returns a modified method of tkinter messagebox or filedialog."""

    def _message_func(*args, **kwargs):
        """Replace the original method of tkinter messagebox or filedialog."""
        root = Tk()
        try:
            root.iconbitmap('favicon.ico')
        except TclError:  # error if file doesn't exist
            pass
        root.title("Do not close this windows! It will close automatically.")
        if withdraw:
            root.withdraw()
        res = getattr(module, item)(*args, **kwargs)
        root.destroy()
        return res

    return _message_func


def _mock_messagebox_func(title: str = None, message: str = None, default: str = None, **options):
    """Mock messagebox method function for IDE."""
    pass


def _mock_filedialog_func(title: str = None, initialdir: str = None, filetypes: List[Tuple[str]] = None, **options):
    """Mock filedialog method function for IDE."""
    pass


class _FileDialog:
    """New tkinter filedialog to avoid empty windows
    that cannot be closed before the end of the program."""

    # Mock attributes
    askdirectory = _mock_filedialog_func
    askopenfile = _mock_filedialog_func
    askopenfilename = _mock_filedialog_func
    askopenfilenames = _mock_filedialog_func
    askopenfiles = _mock_filedialog_func
    asksaveasfile = _mock_filedialog_func
    asksaveasfilename = _mock_filedialog_func

    def __init__(self):
        attr_to_drop = [attr for attr in dir(self) if attr.startswith("ask")]
        for attr in attr_to_drop:
            delattr(_FileDialog, attr)

    def __getattr__(self, item):
        if item.startswith("ask") and item.lower() in dir(f_dialog):
            return _wrapper(f_dialog, item, withdraw=True)
        return getattr(f_dialog, item)


class _MessageBox:
    """New tkinter messagebox to avoid empty windows
    that cannot be closed before the end of the program."""

    # Mock attributes
    askokcancel = _mock_messagebox_func
    askquestion = _mock_messagebox_func
    askretrycancel = _mock_messagebox_func
    askyesno = _mock_messagebox_func
    askyesnocancel = _mock_messagebox_func
    showinfo = _mock_messagebox_func
    showerror = _mock_messagebox_func
    showwarning = _mock_messagebox_func

    showtext = showtext
    askcustomquestion = ask_custom_question
    ask_multiple_questions = ask_multiple_questions
    askoption = ask_option
    _custom_msgbox = {'showtext': showtext, 'askcustomquestion': askcustomquestion,
                      'ask_multiple_questions': ask_multiple_questions, 'askoption': askoption,
                      }

    def __init__(self):
        attr_to_drop = [attr for attr in dir(self) if not attr.startswith("_") and attr.lower() in dir(self)]
        for attr in attr_to_drop:
            delattr(_MessageBox, attr)

    def __getattr__(self, item):
        if item in self._custom_msgbox:
            return self._custom_msgbox[item]
        if not item.startswith("_") and item.lower() in dir(msg_box):
            return _wrapper(msg_box, item, withdraw=True)
        return getattr(msg_box, item)


messagebox = _MessageBox()  # WARN: tkinter messagebox modified
filedialog = _FileDialog()  # WARN: tkinter filedialog modified

# For testing purposes
if __name__ == "__main__":
    # print(msg_box.showinfo('Info (original)'))
    print(messagebox.showinfo('Info (modified)'))
    # print(msg_box.askyesno('Question (original)'))
    print(messagebox.askyesno('Question (modified)'))
    # print(f_dialog.askopenfilenames(title='Yes or No ? (Original)'))
    print(filedialog.askopenfilenames(title='Yes or No ? (Modified)'))
    print(messagebox.showtext(text="Hello!"))
    print(messagebox.askcustomquestion(answers=[1, 2]))
    print(messagebox.ask_multiple_questions(answers=[[1, 2]]))
