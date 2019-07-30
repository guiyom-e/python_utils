# -*- coding: utf-8 -*-
# open source project
"""
Modified messagebox, simpledialog and filedialog (tkinter modules)
to avoid empty Tk windows that cannot be closed before the end of the program.
"""
import tkinter as tk
from collections import OrderedDict
from typing import List, Tuple
import functools

from tkinter import Tk, TclError, ttk
from tkinter import messagebox as msg_box
from tkinter import filedialog as f_dialog
from tkinter import simpledialog as s_dialog

from tools.helpers.interface.basics import CustomTk


def _wrapper(module, item, withdraw=True):
    """Returns a modified method of tkinter messagebox, simpledialog or filedialog."""

    def _message_func(*args, **kwargs):
        """Replace the original method of tkinter messagebox or filedialog."""
        root = CustomTk(title="Do not close this windows! It will close automatically.")
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


def _mock_simpledialog_func(title: str = None, prompt: str = None, **options):
    """Mock simpledialog method function for IDE."""
    pass


class _BaseDialog:
    """Base class for dialog containers classes."""
    _custom_func = {}
    _base_module = None

    def __init__(self):
        attr_to_drop = [attr for attr in dir(self) if attr.startswith(("ask", "show"))]
        for attr in attr_to_drop:
            delattr(self.__class__, attr)

    def __getattr__(self, item):
        if item in self._custom_func:
            return self._custom_func[item]

        if item.startswith(("ask", "show")) and item in dir(self._base_module):
            return _wrapper(self._base_module, item, withdraw=True)
        return getattr(self._base_module, item)


class _FileDialog(_BaseDialog):
    """New tkinter filedialog to avoid empty Tk windows
    that cannot be closed before the end of the program."""

    # Mock attributes
    askdirectory = _mock_filedialog_func
    askopenfile = _mock_filedialog_func
    askopenfilename = _mock_filedialog_func
    askopenfilenames = _mock_filedialog_func
    askopenfiles = _mock_filedialog_func
    asksaveasfile = _mock_filedialog_func
    asksaveasfilename = _mock_filedialog_func

    _base_module = f_dialog


class _SimpleDialog(_BaseDialog):
    """New tkinter simpledialog to avoid empty Tk windows
    that cannot be closed before the end of the program."""
    askfloat = _mock_simpledialog_func
    askinteger = _mock_simpledialog_func
    askstring = _mock_simpledialog_func

    _base_module = s_dialog


class _MessageBox(_BaseDialog):
    """New tkinter messagebox to avoid empty Tk windows
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

    _base_module = msg_box


_messagebox = _MessageBox()  # WARN: tkinter messagebox modified
_filedialog = _FileDialog()  # WARN: tkinter filedialog modified
_simpledialog = _SimpleDialog()  # WARN: tkinter simpledialog modified


class CustomDialog(tk.Toplevel):
    """Class to open custom dialogs. Adapted from tkinter.simpledialog.Dialog. See its doc for more info."""

    def __init__(self, parent=None, title=None, **kwargs):
        tk.Toplevel.__init__(self, parent)
        self.withdraw()

        if not parent:
            parent = tk._default_root
        if parent.winfo_viewable():
            self.transient(parent)

        try:  # Add icon
            self.iconbitmap('tools/favicon.ico')
        except TclError:
            pass

        title = title or ''
        self.title(title)

        self.parent = parent

        self.result = None
        self.result_keys = None

        body = ttk.Frame(self)
        self._frame = self.body(body, **kwargs)
        body.pack(padx=5, pady=5, fill=tk.BOTH, expand=True)
        setattr(body, 'ok', self.ok)
        setattr(body, 'cancel', self.cancel)

        self._buttonbox()
        self.bind("<Escape>", self.cancel)

        if not self._frame:
            self._frame = self
        self.protocol("WM_DELETE_WINDOW", self.cancel)
        if self.parent is not None:
            self.geometry("+%d+%d" % (parent.winfo_rootx() + 50,
                                      parent.winfo_rooty() + 50))

        self.deiconify()  # become visible now
        self._frame.focus_set()
        # wait for window to appear on screen before calling grab_set
        self.wait_visibility()
        self.grab_set()
        self.wait_window(self)

    def destroy(self):
        # self._frame = None
        tk.Toplevel.destroy(self)

    def body(self, master, **kwargs):  # to override
        pass

    def _buttonbox(self):
        box = ttk.Frame(self)
        w = ttk.Button(box, text="OK", width=10, command=self.ok, default=tk.ACTIVE)
        w.pack(side='left', padx=5, pady=5)
        w = ttk.Button(box, text="Cancel", width=10, command=self.cancel)
        w.pack(side='left', padx=5, pady=5)
        self.bind("<Return>", self.ok)
        box.pack()

    def ok(self, _event=None):
        if not self.validate():
            res = _messagebox.askyesno(title="Incomplete answers",
                                       message="Some answers are missing, do you want to continue?")
            if not res:
                self._frame.focus_set()  # put focus back
                return
        self.withdraw()
        self.update_idletasks()
        self.result = self._get_result()
        self.result_keys = self._get_result_keys()
        try:
            self.apply()
        finally:
            self.on_closing()

    def cancel(self, _event=None):
        self.result = None
        self.result_keys = None
        self.on_closing()

    def on_closing(self):
        if self.parent is not None:
            self.parent.focus_set()
        self.destroy()

    def validate(self):
        return getattr(self._frame, 'validate', lambda: True)()

    def apply(self):
        return getattr(self._frame, 'apply', lambda: None)()

    def _get_result(self):
        if self._frame is self:
            return None
        return getattr(self._frame, 'result', None)

    def _get_result_keys(self):
        if self._frame is self:
            return None
        return getattr(self._frame, 'result_keys', None)


def frame_integration(frame: ttk.Frame, okcancel=False):
    """Decorator wrapper to create a Tk window class from a Frame class.

    >>> class MyFrame(ttk.Frame): pass
    >>> class MyDialog(CustomDialog): pass
    >>> FrameIntegratedInDialog = frame_integration(MyFrame)(MyDialog)
    """

    def class_decorator(cls: CustomDialog):
        """Decorator to integrate the frame into a Dialog class. __init__ method is overwritten."""

        class WrappedClass(cls):
            def body(self, master, **kwargs):
                """Widget body"""
                self._frame = frame(master, **kwargs)
                self._frame.pack(fill=tk.BOTH, expand=True)
                return self._frame

        if not okcancel:
            WrappedClass._buttonbox = lambda *_, **__: None

        functools.update_wrapper(WrappedClass, cls, updated=tuple())

        return WrappedClass

    return class_decorator


def integrate_frame_in_dialog(frame, okcancel=False, base_dialog=CustomDialog):
    """Returns a Dialog class which contains an integrated frame."""

    class NewDialog(base_dialog):
        pass

    return frame_integration(frame, okcancel=okcancel)(NewDialog)


def dialog_function(dialog_cls):
    """Decorator wrapper to create a function that open a dialog window and returns its result.

    The function is completely overwritten, except its signature and docstring (see functools.wraps)
    """

    def wrapper(func):
        @functools.wraps(func)
        def n_func(*args, **kwargs):
            root = Tk()
            root.withdraw()
            dialog = dialog_cls(root, *args, **kwargs)
            root.destroy()
            return dialog.result

        return n_func

    return wrapper


def convert_to_dialog(dialog_cls, func=object):
    """Returns a function that open a dialog window and returns its result."""
    return dialog_function(dialog_cls)(func)


def _format_list_to_dict(obj, default_key='value') -> dict:
    """Format inputs lists/dict for custom dialog frames.

    >>> _format_list_to_dict(['a', 'b'])
    OrderedDict([(0, {'value': 'a'}), (1, {'value': 'b'})])
    >>> _format_list_to_dict(['a', {'value': 'b', 'c': 'd'}])
    OrderedDict([(0, {'value': 'a'}), (1, {'value': 'b', 'c': 'd'})])
    >>> _format_list_to_dict({'a': 1, 'b': {'value': 'c'}})
    {'a': {'value': 1}, 'b': {'value': 'c'}}
    >>> _format_list_to_dict({'a': 1, 'b': {'value': 'c'}})
    {'a': {'value': 1}, 'b': {'value': 'c'}}
    >>> _format_list_to_dict([{'a': 1}, {'b': {'value': 'c'}}])
    OrderedDict([(0, {'a': 1, 'value': 0}), (1, {'b': {'value': 'c'}, 'value': 1})])
    """
    obj = obj or OrderedDict()
    if isinstance(obj, list):
        obj = OrderedDict([(i, ele) for i, ele in enumerate(obj)])
    for k in obj:
        if not isinstance(obj[k], dict):  # value used as default value
            obj[k] = {default_key: obj[k]}
        elif default_key not in obj[k]:  # key used as default value
            obj[k][default_key] = k
    return obj


# For testing purposes
if __name__ == "__main__":
    print(_simpledialog.askinteger('Title', 'Enter integer'))
    # print(msg_box.showinfo('Info (original)'))
    print(_messagebox.showinfo('Info (modified)'))
    # print(msg_box.askyesno('Question (original)'))
    print(_messagebox.askyesno('Question (modified)'))
    # print(f_dialog.askopenfilenames(title='Yes or No ? (Original)'))
    print(_filedialog.askopenfilenames(title='Yes or No ? (Modified)'))
