# -*- coding: utf-8 -*-
# open source project
"""
Defines advanced messagebox to select options within multiple choices.
"""
from typing import Union
import tkinter as tk
from tkinter import ttk

from tools.helpers.utils import isiterable
from tools.helpers.interface.wrappers import dialog_function, CustomDialog, frame_integration, _format_list_to_dict
from tools.helpers.interface.tooltip import ToolTip


def _format_answers(answers):
    """Returns a list of tuples [(string to show in messagebox, value returned, tooltip, *args), ...]"""
    if isinstance(answers, (str, int, float, bool)):
        return [{'value': answers}]
    if not isiterable(answers):
        return [{'value': None}]
    n_answers = []
    for answer in answers:
        if isiterable(answer):
            if len(answer) > 2:
                n_answers.append({'name': answer[0], 'value': answer[1], 'tooltip': answer[2]})
            elif len(answer) > 1:
                n_answers.append({'name': answer[0], 'value': answer[1]})
        else:
            n_answers.append({'value': answer})
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

    def __init__(self, master=None, message: str = None, choices: Union[list, dict] = None,
                 auto_quit=True, geometry_manager='pack', geometry_options=None, **options):
        super().__init__(master, **options)
        self.result = None  # Result var
        self.result_keys = ''
        self.result_str = ''
        self.change_res = tk.IntVar(value=0)
        self._auto_destroy = auto_quit
        message = '' if message is None else message
        self._choices = _format_list_to_dict(_format_answers(choices), default_key='value')
        if message:
            ttk.Label(master=self, text=message, wraplengt=290).pack()
        # pack or grid questions
        self._ans_frame = ttk.Frame(master=self)
        self._ans_frame.pack()
        geometry_options = geometry_options or {}
        if geometry_manager not in ('pack', 'grid'):
            geometry_manager = 'pack'
            geometry_options = {}
        nb_columns = geometry_options.pop('nb_columns', _auto_column(len(choices)))
        self.options = []
        for i, (key, config) in enumerate(self._choices.items()):
            name = str(config.get('name', config['value']))
            tooltip = str(config.get('tooltip', ""))
            but = ttk.Button(master=self._ans_frame, text=name, command=self.return_answer(key))
            if tooltip:
                ToolTip(but, tooltip)
            if geometry_manager == 'grid':
                geometry_options['row'] = i // nb_columns
                geometry_options['column'] = i % nb_columns
            getattr(but, geometry_manager)(**geometry_options)
            self.options.append(but)

    def return_answer(self, key):
        def _return_answer():
            self.result_keys = key
            self.result_str = str(self._choices[key].get('name', self._choices[key]['value']))
            self.result = self._choices[key]['value']
            self.change_res.set(self.change_res.get() + 1)
            if self._auto_destroy:  # destroy the master window if possible
                func = getattr(self.master, 'ok', None)
                if not func:
                    func = getattr(self.master, 'destroy', None)
                if func:
                    func()

        return _return_answer

    def validate(self):
        return True


@frame_integration(CustomQuestionFrame, okcancel=False)
class CustomQuestionDialog(CustomDialog):
    """Window which looks like a messagebox window, but with custom answers (list of tuples)."""
    pass


@dialog_function(CustomQuestionDialog)
def ask_custom_question(title: str = None, message: str = None, choices: Union[list, dict] = None, **options):
    pass


# For testing purposes
if __name__ == "__main__":
    msg = 'Which answer would you choose?\n\nThis line is very long, so it is automatically ' \
          'wrapped  by the program which was made by an amazing developer!'
    _answers = ['First possible answer', 2, 3, '4', None, True, ['list']]
    print(ask_custom_question('Custom question', message=msg,
                              choices=_answers))
    print('ok askcustomquestion')
    root = tk.Tk()
    root.withdraw()
    dialog = CustomQuestionDialog(message=msg, choices=_answers)
    root.destroy()
    print(dialog.result, dialog.result_keys)
    print('ok CustomQuestionDialog')
    root2 = tk.Tk()
    frame = CustomQuestionFrame(master=root2, message=msg, choices=_answers)
    frame.pack()
    root2.mainloop()
    print(frame.result)
    print('ok CustomQuestionFrame')
