import inspect
import functools
from typing import Union
import tkinter as tk
from tkinter import Tk, ttk, TclError


class CustomTk(Tk):
    def __init__(self, title=None, **options):
        super().__init__(**options)
        try:  # Add icon
            self.iconbitmap('tools/favicon.ico')
        except TclError:
            import pdb
            pdb.set_trace()
            pass
        self.title('' if title is None else title)


def center(win, width=None, height=None):
    """Centers a tkinter window.
    :param win: the root or Toplevel window to center
    :param width: custom width for center computation
    :param height: custom height for center computation
    """
    win.update_idletasks()
    width = win.winfo_width() if width is None else width
    frm_width = win.winfo_rootx() - win.winfo_x()
    win_width = width + 2 * frm_width
    height = win.winfo_height() if height is None else height
    titlebar_height = win.winfo_rooty() - win.winfo_y()
    win_height = height + titlebar_height + frm_width
    x = win.winfo_screenwidth() // 2 - win_width // 2
    y = win.winfo_screenheight() // 2 - win_height // 2
    win.geometry('+{}+{}'.format(x, y))


class SelectorFrame(ttk.Frame):
    def __init__(self, master, message: str = None, answers: Union[list, dict] = None,
                 initial_value=None, **options):
        super().__init__(master, **options)
        message = '' if message is None else message
        if message:
            self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
            self.label_msg.grid(row=0, column=0, sticky='new', pady=5)
        self.var = tk.StringVar(self)
        answers = answers or []
        if isinstance(answers, dict):
            answers = [val.get('name', key) for key, val in answers.items()]
        self._answers = answers
        self.option = ttk.OptionMenu(self, self.var, initial_value, *answers)
        self.option.grid(row=1, sticky='ew')
        self.var.set('' if initial_value is None else initial_value)  # initial value

    @property
    def res(self):
        return self.var.get()


def frame_integration(frame: ttk.Frame, okcancel=False):
    """Decorator wrapper to create a Tk window class from a Frame class.

    >>> class Frame(ttk.Frame): pass
    >>> class MyTk(tk.Tk): pass
    >>> FrameIntegratedInMyTk = frame_integration(Frame)(MyTk)
    """

    def class_decorator(cls: tk.Tk):
        """Decorator to integrate the frame into a Tk window class. __init__ method is overwritten."""
        sig = inspect.signature(frame.__init__)
        init_args = [arg for arg in sig.parameters
                     if sig.parameters[arg].kind.name == 'POSITIONAL_OR_KEYWORD']

        class WrappedClass(cls):
            def _add_buttons(self):
                pass

        # if on_closing method does not exist
        if 'on_closing' not in vars(cls):
            def on_closing(self):
                self.destroy()

            WrappedClass.on_closing = on_closing

        # if _before_init staticmethod does not exist
        if '_before_init' not in vars(cls):
            def _before_init(*args, **kwargs):
                return args, kwargs

            WrappedClass._before_init = staticmethod(_before_init)

        if okcancel:
            if 'ok_action' not in vars(cls):
                def ok_action(self, *_, **__):
                    self.on_closing()

                WrappedClass.ok_action = ok_action

            if 'cancel_action' not in vars(cls):
                def cancel_action(self, *_, **__):
                    self._cancel_res = None
                    self.on_closing()

                WrappedClass.cancel_action = cancel_action

            def _add_buttons(self):
                self._ok_but = ttk.Button(self, text="OK", command=self.ok_action)
                self._ok_but.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self._cancel_but = ttk.Button(self, text="Cancel", command=self.cancel_action)
                self._cancel_but.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
                self.bind('<Escape>', func=self.cancel_action)
                self.bind("<Return>", func=self.ok_action)

            WrappedClass._add_buttons = _add_buttons

        @functools.wraps(WrappedClass.__init__)
        def __init__(self, *args, **options):
            args, options = self._before_init(*args, **options)
            kwargs = {key: options.pop(key) for key in init_args if key in options}
            super(WrappedClass, self).__init__(**options)

            # in case of button
            self._wildcard = object()
            self._cancel_res = self._wildcard

            kwargs.pop('master', None)
            self._frame = frame(master=self, *args, **kwargs)
            self._frame.pack(fill=tk.BOTH, expand=True)

            self._add_buttons()

            center(self)
            self.lift()

        WrappedClass.__init__ = __init__

        # if res method does not exist in the class and exists in frame class
        if 'res' not in vars(cls) and 'res' in vars(frame):
            def res(self):
                if self._cancel_res is not self._wildcard:  # cancellation
                    return self._cancel_res
                return self._frame.res

            WrappedClass.res = property(res, None, None, frame.res.__doc__)

        # if res_keys method does not exist in the class and exists in frame class
        if 'res_keys' not in vars(cls) and 'res_keys' in vars(frame):
            def res_keys(self):
                if self._cancel_res is not self._wildcard:  # cancellation
                    return self._cancel_res
                return self._frame.res_keys

            WrappedClass.res_keys = property(res_keys, None, None, frame.res_keys.__doc__)

        return WrappedClass

    return class_decorator


def integrate_frame_in_tk(frame, master_tk=tk.Tk):
    """Returns a Tk class which contains an integrated frame."""

    class NewTk(master_tk):
        pass

    return frame_integration(frame)(NewTk)


def dialog_function(tk_cls):
    """Decorator wrapper to create a function that open a dialog window and returns its result.

    The function is completely overwritten, except its signature and docstring (see functools.wraps)
    """

    def wrapper(func):
        @functools.wraps(func)
        def n_func(*args, **kwargs):
            win = tk_cls(*args, **kwargs)
            win.mainloop()
            try:
                win.destroy()
            except TclError:  # if window already destroyed
                pass
            return getattr(win, 'res', None)

        return n_func

    return wrapper


def convert_to_dialog(tk_cls, func=object):
    """Returns a function that open a dialog window and returns its result."""
    return dialog_function(tk_cls)(func)
