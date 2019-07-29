from typing import Union
import tkinter as tk
from tkinter import ttk
from collections import OrderedDict

from tools.logger import logger
from tools.helpers.utils import isinlist
from tools.helpers.interface.wrappers import (frame_integration, dialog_function, convert_to_dialog, CustomDialog,
                                              _format_list_to_dict)
from tools.helpers.interface.tooltip import ToolTip


class OptionMenuFrame(ttk.Frame):
    """Frame with an OptionMenu widget."""

    def __init__(self, master=None, message: str = None, choices: Union[list, dict] = None,
                 initial_value=None, **options):
        """Initialize a OptionMenuFrame widget.

        :param master: parent Dialog object
        :param message: message to show before the selection
        :param choices: list of choices or OrderedDict of choices with the following format:
                        OrderedDict([(key, {'name': str}), ...}
                        All keys are optional.
        :param initial_value: initial value to display
        :param options: for ttk Frame
        """
        # Init
        super().__init__(master, **options)
        message = '' if message is None else str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
        self.label_msg.grid(row=0, column=0, sticky='new', padx=5)
        self._choices = _format_list_to_dict(choices, default_key='value')
        self._choices = [val.get('value', key) for key, val in self._choices.items()]

        self._var = tk.Variable(self, value=initial_value)
        self._changes, self._initial_value = 0, initial_value  # handle case of no choice
        self._ans_frame = ttk.OptionMenu(self, self._var, initial_value, command=self._change_res, *self._choices)
        self._ans_frame.grid(row=0, column=2, rowspan=2, sticky='nsew')
        self._var.set('' if initial_value is None else initial_value)  # initial value

    def _change_res(self, _value):
        self._changes += 1

    @property
    def result(self):
        """Returns the result"""
        return self._var.get()

    @property
    def result_keys(self):
        """Returns the result"""
        return self._var.get()

    def validate(self):
        """Returns whether the entry is correct or not, i.e. if it is in choices"""
        return isinlist(str(self.result_keys), [str(ele) for ele in self._choices])


@frame_integration(OptionMenuFrame, okcancel=True)
class OptionMenuDialog(CustomDialog):
    """Dialog window with an OptionMenu widget."""
    pass


class CheckBoxFrame(ttk.Frame):
    """Frame with checkboxes."""

    def __init__(self, master=None, message: str = None, choices: Union[list, dict] = None,
                 initial_status=False, nb_columns=10, **options):
        """Initialize a CheckBoxFrame widget.

        :param master: parent Dialog object
        :param message: message to show before the selection
        :param choices: list of choices or OrderedDict of choices with the following format:
                        OrderedDict([(key, {'name': str, 'status': bool, 'tooltip': str}), ...}
                        All keys are optional.
        :param nb_columns: max number of columns for check boxes
        :param options: for ttk Frame
        """
        # Init
        super().__init__(master, **options)
        message = '' if message is None else str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
        self.label_msg.grid(row=0, column=0, sticky='new', padx=5)
        self._choices = _format_list_to_dict(choices, default_key='value')

        self.all_var, self.none_var = tk.BooleanVar(value=False), tk.BooleanVar(value=False)
        all_but = ttk.Checkbutton(master=self, text="[All]", variable=self.all_var, command=self.all_command)
        all_but.grid(row=1, column=0)
        none_but = ttk.Checkbutton(master=self, text="[None]", variable=self.none_var, command=self.none_command)
        none_but.grid(row=1, column=1)

        self._ans_frame = ttk.Frame(master=self)
        self._ans_frame.grid(row=0, column=2, rowspan=2, sticky='e')
        for i, (key, config) in enumerate(self._choices.items()):
            name = str(config.get('name', config['value']))
            status = config.get('status', initial_status)
            tooltip = str(config.get('tooltip', ""))
            config['var'] = tk.BooleanVar(value=status)
            box = ttk.Checkbutton(master=self._ans_frame, text=name, variable=config['var'], command=self.check)
            if tooltip:
                ToolTip(box, tooltip)
            config['check_box'] = box
            box.grid(row=i // nb_columns, column=i % nb_columns, sticky='nw')

    def check(self):
        self.all_var.set(False)
        self.none_var.set(False)

    def all_command(self):
        for config in self._choices.values():
            config['var'].set(True)
        self.none_var.set(False)

    def none_command(self):
        for config in self._choices.values():
            config['var'].set(False)
        self.all_var.set(False)

    @property
    def result(self):
        """Returns results"""
        return [self._choices[key]['value'] for key in self.result_keys]

    @property
    def result_keys(self):
        """Returns the key/index value of the result in choices"""
        return [key for key, cfg in self._choices.items() if cfg['var'].get() is True]

    def validate(self):
        """Returns whether the entry is correct or not: for check box, the answer is always True."""
        return True


@frame_integration(CheckBoxFrame, okcancel=True)
class CheckBoxSelectorDialog(CustomDialog):
    """Dialog window with checkboxes."""
    pass


class RadioButtonFrame(ttk.Frame):
    """Frame with radio buttons."""

    def __init__(self, master=None, message: str = None, choices: Union[list, dict] = None,
                 initial_value=None, nb_columns=10, **options):
        """Initialize a RadioButtonFrame widget.

        :param master: parent Dialog object
        :param message: message to show before the selection
        :param choices: list of choices or OrderedDict of choices with the following format:
                        OrderedDict([(key, {'name': str, 'status': bool, 'tooltip': str}), ...}
                        All keys are optional.
        :param nb_columns: max number of columns for radio buttons
        :param options: for ttk Frame
        """
        # Init
        super().__init__(master, **options)
        message = '' if message is None else str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
        self.label_msg.grid(row=0, column=0, sticky='new', padx=5)
        self._choices = _format_list_to_dict(choices, default_key='value')

        self._var = tk.Variable(value=initial_value)
        self._changes, self._initial_value = 0, initial_value  # handle case of no choice
        self._ans_frame = ttk.Frame(master=self)
        self._ans_frame.grid(row=0, column=2, rowspan=2, sticky='e')
        for i, (key, config) in enumerate(self._choices.items()):
            name = str(config.get('name', config['value']))
            tooltip = str(config.get('tooltip', ""))
            box = ttk.Radiobutton(self._ans_frame, text=name, variable=self._var, value=key,
                                  command=self._change_res)
            if tooltip:
                ToolTip(box, tooltip)
            box.grid(row=i // nb_columns, column=i % nb_columns, sticky='nw')

    def _change_res(self):
        self._changes += 1

    @property
    def result(self):
        """Returns result"""
        if not self._changes:
            return self._initial_value
        key = self.result_keys
        try:
            res = self._choices[key]['value']
        except KeyError as err_msg:
            logger.exception(err_msg)
            logger.error("Bad key '{}' for Radiobutton widget. Use a string or int as key to avoid this error.\n"
                         "None value is returned".format(key))
            return None
        return res

    @property
    def result_keys(self):
        """Returns the key/index value of the result in choices"""
        if not self._changes and self._initial_value is None:  # special case
            return None
        return self._var.get()

    def validate(self):
        """Returns whether the entry is correct or not, i.e. if the answer value is in choices values"""
        return isinlist(self.result, [cfg['value'] for cfg in self._choices.values()])


@frame_integration(RadioButtonFrame, okcancel=True)
class RadioSelectorDialog(CustomDialog):
    """Dialog window with radio buttons."""
    pass


class MultiSelectorFrame(ttk.Frame):
    """Frame with multiple checkboxes, radio buttons or option menu."""

    def __init__(self, master=None, message: str = None, multi_choices: Union[list, dict] = None,
                 initial_status=False, initial_value=None, nb_columns=10, default_box_type='check_box', **options):
        """

        :param master: parent Dialog object
        :param message: message to show before the selection
        :param multi_choices: list of lists of choices or OrderedDict of choices with the following format:
                        OrderedDict([(key, {'name': str, 'tooltip': str, 'choices': Union[OrderedDict, list],
                                            'initial_status': bool, 'box_type': 'radio' OR 'check_box'}), ...}
                        All keys are optional.
        :param options:
        """
        # Init
        super().__init__(master, **options)
        message = '' if message is None else str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
        self.label_msg.grid(row=0, column=0, sticky='new', pady=5)
        self._choices = _format_list_to_dict(multi_choices, default_key='choices')

        self._ans_frame = ttk.Frame(master=self)
        self._ans_frame.grid(row=1, column=0, columnspan=2, sticky='new')
        for i, (key, config) in enumerate(self._choices.items()):
            name = str(config.get('name', key))
            tooltip = str(config.get('tooltip', ""))
            choices = config.get('choices', config)
            box_type = config.get('box_type', default_box_type)
            if box_type == 'check_box':
                initial_status = config.get('initial_status', initial_status)
                answer = CheckBoxFrame(self._ans_frame, message=name, choices=choices,
                                       nb_columns=nb_columns, initial_status=initial_status)
            elif box_type == 'radio':
                initial_value = config.get('initial_value', initial_value)
                answer = RadioButtonFrame(self._ans_frame, message=name, choices=choices,
                                          nb_columns=nb_columns, initial_value=initial_value)
            elif box_type == 'selector':
                initial_value = config.get('initial_value', initial_value)
                answer = OptionMenuFrame(self._ans_frame, message=name, choices=choices,
                                         initial_value=initial_value)
            else:
                raise ValueError(box_type)
            if tooltip:
                ToolTip(answer.label_msg, tooltip)
            answer.grid(row=i, sticky='nw', pady=5)
            config['selector'] = answer

    @property
    def result(self):
        """Returns the results"""
        return OrderedDict([(key, cfg['selector'].result) for key, cfg in self._choices.items()])

    @property
    def result_keys(self):
        """Returns the key/index value of the result in multi_choices"""
        return OrderedDict([(key, cfg['selector'].result_keys) for key, cfg in self._choices.items()])

    def validate(self):
        return all(getattr(cfg['selector'], 'validate', True)() for cfg in self._choices.values())


@frame_integration(MultiSelectorFrame, okcancel=True)
class MultiSelectorDialog(CustomDialog):
    """Window which looks like a messagebox window, but with custom choices (list of tuples)."""
    pass


@dialog_function(OptionMenuDialog)
def ask_option(title: str = None, message: str = None, choices: Union[list, dict] = None,
               initial_value: bool = None, **options):
    pass


@dialog_function(CheckBoxSelectorDialog)
def ask_checkbox(title: str = None, message: str = None, choices: Union[list, dict] = None,
                 initial_status: bool = None, **options):
    pass


@dialog_function(RadioSelectorDialog)
def ask_radio_button(title: str = None, message: str = None, choices: Union[list, dict] = None,
                     initial_value: bool = None, **options):
    pass


@dialog_function(MultiSelectorDialog)
def ask_multiple_questions(title: str = None, message: str = None, multi_choices: Union[list, dict] = None,
                           initial_status: bool = False, **options):
    pass


if __name__ == '__main__':
    import numpy as np
    from copy import deepcopy
    import pandas as pd

    # Test OptionMenuDialog
    print(convert_to_dialog(OptionMenuDialog)(title='test', message='Question',
                                              choices=[5, 'r', pd.DataFrame(), [3, 5], None]))
    # Test CheckBoxSelectorDialog
    print(convert_to_dialog(CheckBoxSelectorDialog)(title='test', message='Question',
                                                    choices={5: {'tooltip': 8}, 'r': 't'}))
    # Test RadioSelectorDialog
    _root = tk.Tk()
    _root.withdraw()
    _dialog = RadioSelectorDialog(parent=None, title='test', message='Question',
                                  choices=[{'name': 5, 'value': 8}, 'r', pd.DataFrame()], initial_value="init")
    _root.destroy()
    print("result_keys: {}\nresult: {}".format(_dialog.result_keys, _dialog.result))

    # Test MultiSelectorDialog
    _dico = {'foo': {'name': 'bar', 'value': 'zoo', 'tooltip': 'tap'}, 'e': {'status': True},
             8: {'tooltip': 'hey'}, None: {},  # WARN: None should not be a key (error with tk.Variable)
             'f': {}, 'u': {}, 9: {'name': 8, 'value': 8}}
    _dico.update({round(i * np.pi, 2 * int(((np.pi * 10 ** (i + 1)) - int(np.pi * 10 ** i) * 10))): {}
                  for i in range(30)})
    _answers = {'hi': {'choices': _dico, 'tooltip': 'zulu'},
                'b': {'name': 'name', 'box_type': 'radio', 'choices': deepcopy(_dico), 'initial_value': 8},
                'c': {'name': 'yo', 'box_type': 'selector', 'choices': deepcopy(_dico)}}
    print(ask_multiple_questions(multi_choices=_answers))
