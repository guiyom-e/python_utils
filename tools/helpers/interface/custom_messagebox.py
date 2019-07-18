# open source
from typing import Union
import tkinter as tk
from tkinter import ttk, TclError

from tools.helpers.utils import isiterable
from tools.helpers.interface.tooltip import ToolTip


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


def _format_answers(answers):
    """Returns a list of tuples [(string to show in messagebox, value returned, tooltip, *args), ...]"""
    if isinstance(answers, (str, int, float, bool)):
        return [(str(answers), answers)]
    if not isiterable(answers):
        return [('None', None)]
    n_answers = []
    for answer in answers:
        if isiterable(answer) and len(answer) >= 2:
            n_answers.append((str(answer[0]), *answer[1:]))
        else:
            n_answers.append((str(answer), answer, ""))
    return n_answers


def _auto_column(length, default=3):
    """Pretty number of columns."""
    if length <= 0:
        return 1
    elif length <= 3:
        return length
    elif length == 4:
        return 2
    elif length // 4 == 0:
        return 4
    elif length // 3 == 0:
        return 3
    elif length // 2 == 0:
        return 2
    else:
        return default


class CustomQuestionFrame(ttk.Frame):
    """Frame with custom answers displayed as tkinter buttons."""
    def __init__(self, master=None, message: str = None, answers: Union[list, dict] = None,
                 auto_quit=True, geometry_manager='pack', geometry_options=None, **options):
        super().__init__(master, **options)
        self.res = None  # Result var
        self.res_str = ''
        self.change_res = tk.IntVar(value=0)
        self._auto_destroy = auto_quit
        message = '' if message is None else message
        self._answers = _format_answers(answers)
        if message:
            ttk.Label(master=self, text=message, wraplengt=290).pack()
        # pack or grid questions
        self._ans_frame = ttk.Frame(master=self)
        self._ans_frame.pack()
        geometry_options = geometry_options or {}
        if geometry_manager not in ('pack', 'grid'):
            geometry_manager = 'pack'
            geometry_options = {}
        nb_columns = geometry_options.pop('nb_columns', _auto_column(len(answers)))
        self.options = []
        for i, answer in enumerate(self._answers):
            but = ttk.Button(master=self._ans_frame, text=answer[0], command=self.return_answer(answer))
            if len(answer) >= 3 and answer[2]:
                ToolTip(but, answer[2])
            if geometry_manager == 'grid':
                geometry_options['row'] = i // nb_columns
                geometry_options['column'] = i % nb_columns
            getattr(but, geometry_manager)(**geometry_options)
            self.options.append(but)

    def return_answer(self, answer):
        def _return_answer():
            self.res_str = answer[0]
            self.res = answer[1]
            self.change_res.set(self.change_res.get() + 1)
            if self._auto_destroy:
                self.master.destroy()

        return _return_answer


class CustomQuestion(tk.Tk):
    """Window which looks like a messagebox window, but with custom answers (list of tuples)."""
    def __init__(self, title: str = None, message: str = None, answers: Union[list, dict] = None,
                 icon_path: str = 'tools/favicon.ico', **options):
        super().__init__(**options)
        self.withdraw()  # Hide the window et first time
        try:  # Add icon
            self.iconbitmap(icon_path)
        except TclError:
            pass
        self.title('' if title is None else title)
        self._frame = CustomQuestionFrame(master=self, message=message, answers=answers)
        self._frame.grid(column=0, row=0, sticky="nsew")
        self.columnconfigure(0, weight=1, minsize=300)
        self.rowconfigure(0, weight=1, minsize=200)
        center(self)
        self.deiconify()
        self.lift()

    def return_answer(self, answer):
        return self._frame.return_answer(answer)

    @property
    def res(self):
        return self._frame.res

    @property
    def res_str(self):
        return self._frame.res_str

    @property
    def change_res(self):
        return self._frame.change_res


def ask_custom_question(title: str = None, message: str = None, answers: Union[list, dict] = None, **options):
    win = CustomQuestion(title, message, answers, **options)
    win.mainloop()
    try:
        win.destroy()
    except TclError:  # if window already destroyed
        pass
    return win.res


# For testing purposes
if __name__ == "__main__":
    msg = 'Which answer would you choose?\n\nThis line is very long, so it is automatically ' \
          'wrapped  by the program which was made by an amazing developer!'
    _answers = ['First possible answer', 2, 3, '4', None, True, ['list']]
    print(ask_custom_question('Custom question', message=msg,
                              answers=_answers))
    print('ok ask_custom_question')
    root = CustomQuestion(message=msg, answers=_answers)
    root.mainloop()
    # root.destroy()
    print(root.res, root.change_res.get())
    print('ok CustomQuestion')
    root2 = tk.Tk()
    frame = CustomQuestionFrame(master=root2, message=msg, answers=_answers)
    frame.pack()
    root2.mainloop()
    print(frame.res, frame.change_res.get())
    print('ok CustomQuestionFrame')
