# -*- coding: utf-8 -*-
# open source project
"""
Defines a dialog to select a date with a calendar.
"""
# Original author: Miguel Martinez Lopez
# Version: 1.0.7
# Adapted in 2019-04 (added: integration in a Frame, date interval selection, dialog; changed: minor visual changes)
# No more compatibility with Python 2


import sys
import calendar
import datetime
import pandas as pd
from typing import Union, List, Tuple  # not compatible with Python2

import tkinter as tk
import tkinter.font as tkFont
import tkinter.ttk as ttk

from tkinter.constants import CENTER, LEFT, N, E, W, S
from tkinter import StringVar
from tkinter import messagebox  # original messagebox from tkinter

from tools.logger import logger
from tools.helpers.interface.basics import CustomTk
from tools.helpers.interface.anomalies import raise_anomaly
from tools.helpers.interface.wrappers import (frame_integration, dialog_function, CustomDialog, _format_list_to_dict)


def _get_calendar(locale, fwday):
    # instantiate proper calendar class
    if locale is None:
        return calendar.TextCalendar(fwday)
    else:
        return calendar.LocaleTextCalendar(fwday, locale)


class Calendar(ttk.Frame):
    datetime = calendar.datetime.datetime
    timedelta = calendar.datetime.timedelta

    def __init__(self, master=None, year=None, month=None, firstweekday=calendar.MONDAY, locale=None,
                 activebackground='#b1dcfb', activeforeground='black', selectbackground='#003eff',
                 selectforeground='white', command=None, borderwidth=1, relief="solid", on_click_month_button=None):
        """
        WIDGET OPTIONS

            locale, firstweekday, year, month, selectbackground,
            selectforeground, activebackground, activeforeground,
            command, borderwidth, relief, on_click_month_button
        """

        if year is None:
            year = self.datetime.now().year

        if month is None:
            month = self.datetime.now().month

        self._selected_date = None

        self._sel_bg = selectbackground
        self._sel_fg = selectforeground

        self._act_bg = activebackground
        self._act_fg = activeforeground

        self.on_click_month_button = on_click_month_button

        self._selection_is_visible = False
        self._command = command

        ttk.Frame.__init__(self, master, borderwidth=borderwidth, relief=relief)

        self.bind("<FocusIn>", lambda event: self.event_generate('<<DatePickerFocusIn>>'))
        self.bind("<FocusOut>", lambda event: self.event_generate('<<DatePickerFocusOut>>'))

        self._cal = _get_calendar(locale, firstweekday)

        # custom ttk styles
        style = ttk.Style(master)
        style.layout('L.TButton', (
            [('Button.focus', {'children': [('Button.leftarrow', None)]})]
        ))
        style.layout('R.TButton', (
            [('Button.focus', {'children': [('Button.rightarrow', None)]})]
        ))

        self._font = tkFont.Font(master)

        self._header_var = StringVar(master)

        # header frame and its widgets
        hframe = ttk.Frame(self)
        lbtn = ttk.Button(hframe, style='L.TButton', command=self._on_press_left_button)
        lbtn.pack(side=LEFT)

        self._header = ttk.Label(hframe, width=15, anchor=CENTER, textvariable=self._header_var)
        self._header.pack(side=LEFT, padx=12)

        rbtn = ttk.Button(hframe, style='R.TButton', command=self._on_press_right_button)
        rbtn.pack(side=LEFT)
        hframe.grid(columnspan=7, pady=4)

        self._day_labels = {}

        days_of_the_week = self._cal.formatweekheader(3).split()

        for i, day_of_the_week in enumerate(days_of_the_week):
            ttk.Label(self, text=day_of_the_week, background='grey90').grid(row=1, column=i, sticky=N + E + W + S)

        for i in range(6):
            for j in range(7):
                self._day_labels[i, j] = label = tk.Label(self, background="white")

                label.grid(row=i + 2, column=j, sticky=N + E + W + S)
                label.bind("<Enter>",
                           lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
                label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

                label.bind("<1>", self._pressed)

        # adjust its columns width
        font = tkFont.Font(master)
        maxwidth = max(font.measure(text) for text in days_of_the_week)
        for i in range(7):
            self.grid_columnconfigure(i, minsize=maxwidth, weight=1)

        self._year = None
        self._month = None

        # insert dates in the currently empty calendar
        self._build_calendar(year, month)

    def _build_calendar(self, year, month):
        if not (self._year == year and self._month == month):
            self._year = year
            self._month = month

            # update header text (Month, YEAR)
            header = self._cal.formatmonthname(year, month, 0)
            self._header_var.set(header.title())

            # update calendar shown dates
            cal = self._cal.monthdayscalendar(year, month)

            for i in range(len(cal)):

                week = cal[i]
                fmt_week = [('%02d' % day) if day else '' for day in week]

                for j, day_number in enumerate(fmt_week):
                    self._day_labels[i, j]["text"] = day_number

            if len(cal) < 6:
                for j in range(7):
                    self._day_labels[5, j]["text"] = ""

        if self._selected_date is not None and self._selected_date.year == self._year and self._selected_date.month == self._month:
            self._show_selection()

    def _find_label_coordinates(self, date):
        first_weekday_of_the_month = (date.weekday() - date.day) % 7

        return divmod((first_weekday_of_the_month - self._cal.firstweekday) % 7 + date.day, 7)

    def _show_selection(self):
        """Show a new selection."""

        i, j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i, j]

        label.configure(background=self._sel_bg, foreground=self._sel_fg)

        label.unbind("<Enter>")
        label.unbind("<Leave>")

        self._selection_is_visible = True

    def _clear_selection(self):
        """Show a new selection."""
        i, j = self._find_label_coordinates(self._selected_date)

        label = self._day_labels[i, j]
        label.configure(background="white", foreground="black")

        label.bind("<Enter>", lambda event: event.widget.configure(background=self._act_bg, foreground=self._act_fg))
        label.bind("<Leave>", lambda event: event.widget.configure(background="white"))

        self._selection_is_visible = False

    # Callback

    def _pressed(self, evt):
        """Clicked somewhere in the calendar."""

        text = evt.widget["text"]

        if text == "":
            return

        day_number = int(text)

        new_selected_date = datetime.datetime(self._year, self._month, day_number)
        if self._selected_date != new_selected_date:
            if self._selected_date is not None:
                self._clear_selection()

            self._selected_date = new_selected_date

            self._show_selection()

        if self._command:
            self._command(self._selected_date)

    def _on_press_left_button(self):
        self.prev_month()

        if self.on_click_month_button is not None:
            self.on_click_month_button()

    def _on_press_right_button(self):
        self.next_month()

        if self.on_click_month_button is not None:
            self.on_click_month_button()

    def select_prev_day(self):
        """Updated calendar to show the previous day."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month)  # reconstruct calendar

    def select_next_day(self):
        """Update calendar to show the next day."""

        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=1)

        self._build_calendar(self._selected_date.year, self._selected_date.month)  # reconstruct calendar

    def select_prev_week_day(self):
        """Updated calendar to show the previous week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date - self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month)  # reconstruct calendar

    def select_next_week_day(self):
        """Update calendar to show the next week."""
        if self._selected_date is None:
            self._selected_date = datetime.datetime(self._year, self._month, 1)
        else:
            self._clear_selection()
            self._selected_date = self._selected_date + self.timedelta(days=7)

        self._build_calendar(self._selected_date.year, self._selected_date.month)  # reconstruct calendar

    def select_current_date(self):
        """Update calendar to current date."""
        if self._selection_is_visible: self._clear_selection()

        self._selected_date = datetime.datetime.now()
        self._build_calendar(self._selected_date.year, self._selected_date.month)

    def prev_month(self):
        """Updated calendar to show the previous week."""
        if self._selection_is_visible: self._clear_selection()

        date = self.datetime(self._year, self._month, 1) - self.timedelta(days=1)
        self._build_calendar(date.year, date.month)  # reconstuct calendar

    def next_month(self):
        """Update calendar to show the next month."""
        if self._selection_is_visible: self._clear_selection()

        date = self.datetime(self._year, self._month, 1) + \
               self.timedelta(days=calendar.monthrange(self._year, self._month)[1] + 1)

        self._build_calendar(date.year, date.month)  # reconstuct calendar

    def prev_year(self):
        """Updated calendar to show the previous year."""

        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year - 1, self._month)  # reconstruct calendar

    def next_year(self):
        """Update calendar to show the next year."""

        if self._selection_is_visible: self._clear_selection()

        self._build_calendar(self._year + 1, self._month)  # reconstruct calendar

    def get_selection(self):
        """Return a datetime representing the current selected date."""
        return self._selected_date

    selection = get_selection

    def set_selection(self, date):
        """Set the selected date."""
        if self._selected_date is not None and self._selected_date != date:
            self._clear_selection()

        self._selected_date = date

        self._build_calendar(date.year, date.month)  # reconstruct calendar


# see this URL for date format information:
#     https://docs.python.org/3/library/datetime.html#strftime-strptime-behavior

class Datepicker(ttk.Entry):
    def __init__(self, master, entrywidth=None, entrystyle=None, datevar=None, dateformat="%Y-%m-%d", onselect=None,
                 firstweekday=calendar.MONDAY, locale=None, activebackground='#b1dcfb', activeforeground='black',
                 selectbackground='#003eff', selectforeground='white', borderwidth=1, relief="solid"):
        """tkinter Entry with a calendar.

        These are the default bindings:
            Click button 1 on entry: Show calendar
            Click button 1 outside calendar and entry: Hide calendar
            Escape: Hide calendar
            CTRL + PAGE UP: Move to the previous month.
            CTRL + PAGE DOWN: Move to the next month.
            CTRL + SHIFT + PAGE UP: Move to the previous year.
            CTRL + SHIFT + PAGE DOWN: Move to the next year.
            CTRL + LEFT: Move to the previous day.
            CTRL + RIGHT: Move to the next day.
            CTRL + UP: Move to the previous week.
            CTRL + DOWN: Move to the next week.
            CTRL + END: Close the datepicker and erase the date.
            CTRL + HOME: Move to the current month.
            CTRL + SPACE: Show date on calendar
            CTRL + Return: Set current selection to entry
        """
        if datevar is not None:
            self.date_var = datevar
        else:
            self.date_var = tk.StringVar(master)

        entry_config = {}
        if entrywidth is not None:
            entry_config["width"] = entrywidth

        if entrystyle is not None:
            entry_config["style"] = entrystyle

        ttk.Entry.__init__(self, master, textvariable=self.date_var, **entry_config)

        self.date_format = dateformat

        self._is_calendar_visible = False
        self._on_select_date_command = onselect
        self.calendar_frame = Calendar(master, firstweekday=firstweekday, locale=locale,
                                       activebackground=activebackground, activeforeground=activeforeground,
                                       selectbackground=selectbackground, selectforeground=selectforeground,
                                       command=self._on_selected_date, on_click_month_button=lambda: self.focus())
        self.bind_all("<1>", self._on_click, "+")

        self.bind("<FocusOut>", lambda event: self._on_entry_focus_out())
        self.bind("<Escape>", lambda event: self.hide_calendar())
        self.calendar_frame.bind("<<DatePickerFocusOut>>", lambda event: self._on_calendar_focus_out())

        # CTRL + PAGE UP: Move to the previous month.
        self.bind("<Control-Prior>", lambda event: self.calendar_frame.prev_month())

        # CTRL + PAGE DOWN: Move to the next month.
        self.bind("<Control-Next>", lambda event: self.calendar_frame.next_month())

        # CTRL + SHIFT + PAGE UP: Move to the previous year.
        self.bind("<Control-Shift-Prior>", lambda event: self.calendar_frame.prev_year())

        # CTRL + SHIFT + PAGE DOWN: Move to the next year.
        self.bind("<Control-Shift-Next>", lambda event: self.calendar_frame.next_year())

        # CTRL + LEFT: Move to the previous day.
        self.bind("<Control-Left>", lambda event: self.calendar_frame.select_prev_day())

        # CTRL + RIGHT: Move to the next day.
        self.bind("<Control-Right>", lambda event: self.calendar_frame.select_next_day())

        # CTRL + UP: Move to the previous week.
        self.bind("<Control-Up>", lambda event: self.calendar_frame.select_prev_week_day())

        # CTRL + DOWN: Move to the next week.
        self.bind("<Control-Down>", lambda event: self.calendar_frame.select_next_week_day())

        # CTRL + END: Close the datepicker and erase the date.
        self.bind("<Control-End>", lambda event: self.erase())

        # CTRL + HOME: Move to the current month.
        self.bind("<Control-Home>", lambda event: self.calendar_frame.select_current_date())

        # CTRL + SPACE: Show date on calendar
        self.bind("<Control-space>", lambda event: self.show_date_on_calendar())

        # CTRL + Return: Set to entry current selection
        self.bind("<Control-Return>", lambda event: self.set_date_from_calendar())

    def set_date_from_calendar(self):
        if self.is_calendar_visible:
            selected_date = self.calendar_frame.selection()

            if selected_date is not None:
                self.date_var.set(selected_date.strftime(self.date_format))

                if self._on_select_date_command is not None:
                    self._on_select_date_command(selected_date)

            self.hide_calendar()

    @property
    def current_text(self):
        return self.date_var.get()

    @current_text.setter
    def current_text(self, text):
        self.date_var.set(text)

    @property
    def current_date(self):
        try:
            date = datetime.datetime.strptime(self.date_var.get(), self.date_format)
            return date
        except ValueError:
            return None

    @current_date.setter
    def current_date(self, date):
        self.date_var.set(date.strftime(self.date_format))

    @property
    def is_valid_date(self):
        if self.current_date is None:
            return False
        else:
            return True

    def show_date_on_calendar(self):
        date = self.current_date
        if date is not None:
            self.calendar_frame.set_selection(date)

        self.show_calendar()

    def show_calendar(self):
        if not self._is_calendar_visible:
            self.calendar_frame.place(in_=self, relx=0, rely=1)
            self.calendar_frame.lift()

        self._is_calendar_visible = True

    def hide_calendar(self):
        if self._is_calendar_visible:
            self.calendar_frame.place_forget()

        self._is_calendar_visible = False

    def erase(self):
        self.hide_calendar()
        self.date_var.set("")

    @property
    def is_calendar_visible(self):
        return self._is_calendar_visible

    def _on_entry_focus_out(self):
        if not str(self.focus_get()).startswith(str(self.calendar_frame)):
            self.hide_calendar()

    def _on_calendar_focus_out(self):
        if self.focus_get() != self:
            self.hide_calendar()

    def _on_selected_date(self, date):
        self.date_var.set(date.strftime(self.date_format))
        self.hide_calendar()

        if self._on_select_date_command is not None:
            self._on_select_date_command(date)

    def _on_click(self, event):
        str_widget = str(event.widget)

        if str_widget == str(self):
            if not self._is_calendar_visible:
                self.show_date_on_calendar()
        else:
            if not str_widget.startswith(str(self.calendar_frame)) and self._is_calendar_visible:
                self.hide_calendar()


class DatePickerFrame(ttk.Frame):
    """Integration of DatePicker in a Frame"""

    def _init_date_picker(self, initial_value):
        if initial_value is None:
            initial_value = datetime.datetime.now()
        if isinstance(initial_value, datetime.datetime):
            self.date_picker.current_date = initial_value
            self.date_picker.current_text = initial_value.strftime(self.dateformat)
        else:
            self.date_picker.date_var.set(None)
            self.date_picker.current_text = ""

    def __init__(self, master=None, message: str = None, initial_value=None,
                 dateformat=None, **options):
        """Initialization method

        :param master: parent ttk Frame object
        :param message: message to show before the selection
        :param initial_value: default date. If None, the date of the day is used.
        :param dateformat: date format string (ISO 8601 format "%Y-%m-%d by default)
        :param bypass_dialog: if True, the initial_value is directly returned without dialog
        :param options: options for parent
        """
        # Init
        super().__init__(master, **options)
        message = "Date entry" if message is None else str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290, justify="left", )
        self.label_msg.grid(row=0, column=0, sticky='new', padx=5)

        self.dateformat = dateformat or "%Y-%m-%d"
        self.date_picker = Datepicker(self, dateformat=self.dateformat)
        self._init_date_picker(initial_value)
        self.date_picker.grid(row=1, column=0, sticky=N + W, pady=5, padx=5)
        self.grid_columnconfigure(0, pad=110, weight=1)
        self.grid_rowconfigure(1, pad=180, weight=1)

    @property
    def result(self):
        """Returns result: current date"""
        return self.date_picker.current_date

    @property
    def result_keys(self):
        """Returns the text value of the result"""
        return self.date_picker.current_text

    def validate(self):
        """Returns whether the entry is correct or not: for check box, the answer is always True."""
        return self.date_picker.is_valid_date


class DateSelectorFrame(ttk.Frame):
    """Two date pickers selecting dates from a start date (included) to an end date (excluded)

    If a date is empty, the considered value is None and dates are not filtered.
    """

    def __init__(self, master=None, message=None, mode='auto', choices=None,
                 date_start=None, date_end=None, dateformat=None, allow_empty=True, **options):
        """Initialization method

        :param master: parent ttk Frame object
        :param message: message to show before the selection
        :param mode: 'tuple': returns the dates chosen by the user,
        'filter': return the list of dates filtered dates in choices with the dates chosen by the user,
        'auto' (default value): if choices is None, use 'tuple' mode, otherwise use 'filter' mode.
        :param choices: list of dates or OrderedDict of choices with the following format:
                        OrderedDict([(key, {'name': str, 'value': datetime.datetime}), ...}
                        All keys are optional.
        :param date_start: default start date. If None, the earliest date of choices is used.
        :param date_end: default end date. If None, the latest date of choices is used. If no choices, empty date.
        :param dateformat: date format string (ISO 8601 format "%Y-%m-%d by default)
        :param allow_empty: if True, empty dates are allowed (considered as None values)
        :param options: options for parent
        """
        # Init
        super().__init__(master, **options)
        if mode == 'auto' or mode is None:
            mode = 'tuple' if choices is None else 'filter'
        self.mode = mode
        self.allow_empty = allow_empty
        dateformat = dateformat or "%Y-%m-%d"
        self._choices = _format_list_to_dict(choices, default_key='value')
        self._dates = [v['value'] for v in self._choices.values()
                       if isinstance(v['value'], datetime.datetime) and v['value'] is not pd.NaT]
        if self._dates:
            self._min_date = min(self._dates)  # for comparison
            self._max_date = max(self._dates) + datetime.timedelta(days=1)
            min_str = self._min_date.strftime(dateformat)  # for display
            max_str = self._max_date.strftime(dateformat)
            date_start = date_start or self._min_date  # for default date
            date_end = date_end or self._max_date
        else:
            self._min_date, self._max_date = datetime.datetime.now(), datetime.datetime.now()
            min_str, max_str = 'NaT', 'NaT'
            date_start = date_start or ''
            date_end = date_end or ''

        if message is None:
            message = 'Select dates from {} to {}'.format(min_str, max_str) if mode == 'filter' else ''
        else:
            message = str(message)
        self.label_msg = ttk.Label(master=self, text=message, wraplengt=290)
        self.label_msg.grid(row=0, column=0, columnspan=2, sticky='new', padx=5)

        self._start_date_frame = DatePickerFrame(self, message="Start date (included)",
                                                 initial_value=date_start, dateformat=dateformat)
        self._start_date_frame.grid(row=1, column=0, sticky='new', padx=5)

        self._end_date_frame = DatePickerFrame(self, message="End date (excluded)",
                                               initial_value=date_end, dateformat=dateformat)
        self._end_date_frame.grid(row=1, column=1, sticky='new', padx=5)

    @property
    def filtered_result(self) -> List[datetime.datetime]:
        """Returns the dates in choices filtered"""
        date_min = self._start_date_frame.result
        date_max = self._end_date_frame.result
        return [date for date in self._dates if (date_min or self._min_date) <= date < (date_max or self._max_date)]

    @property
    def result(self):
        """Returns result: filtered dates or tuple of selected dates"""
        return self.filtered_result if self.mode == 'filter' else self.result_keys

    @property
    def result_keys(self) -> Tuple[Union[datetime.datetime, None], Union[datetime.datetime, None]]:
        """Returns the two dates defining the interval"""
        return self._start_date_frame.result, self._end_date_frame.result

    def validate(self):
        """Returns whether the entry is correct or not: for check box, the answer is always True."""
        entry_start = self._start_date_frame.date_picker.date_var.get()
        entry_end = self._end_date_frame.date_picker.date_var.get()
        if entry_start == entry_end == '':
            return True if self.allow_empty else False
        if self._start_date_frame.validate() and entry_end == '':
            return True if self.allow_empty else False
        if self._end_date_frame.validate() and entry_start == '':
            return True if self.allow_empty else False
        return self._start_date_frame.validate() and self._end_date_frame.validate() \
               and self._start_date_frame.result <= self._end_date_frame.result


@frame_integration(DatePickerFrame, okcancel=True)
class DatePickerDialog(CustomDialog):
    """Dialog window with date picker."""
    pass


@frame_integration(DateSelectorFrame, okcancel=True)
class DateSelectorDialog(CustomDialog):
    """Dialog window with two date pickers to select dates inside a time period."""
    pass


@dialog_function(DatePickerDialog)
def askdate(title: str = None, message: str = None, initial_value: datetime.datetime = None, **options):
    """Ask a date to the user.

    :param title: window title
    :param message: message to show before the entry of dialog
    :param initial_value: first date to show in the entry of dialog. If None the current date is used.
    :param bypass_dialog: if True, no dialog is opened and the function is executed, returning either:
        * initial_value if initial_value is as date (datetime.datetime type)
        * the current date if initial_value is None
        * None in the other cases
    :param options: options for the dialog class
    :return: datetime.datetime object or None
    """
    if initial_value is None:
        initial_value = datetime.datetime.now()
    if not isinstance(initial_value, datetime.datetime):
        initial_value = None
    return initial_value


@dialog_function(DateSelectorDialog)
def askperiod(title: str = None, message: str = None, mode: str = 'auto', choices: Union[list, dict] = None,
              date_start: datetime.datetime = None, date_end: datetime.datetime = None, dateformat: str = None,
              **options):
    if mode == 'auto':
        mode = 'filter' if choices else 'tuple'
    if mode == 'tuple':
        return date_start, date_end
    else:
        logger.debug("No default answer for 'askperiod' dialog with mode 'filter'. None value is returned.")
        return None


class MainDateTk(CustomTk):  # obsolete
    def __init__(self):
        super().__init__()
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def on_closing(self):
        res = messagebox.askyesnocancel(message="Do you want to select this date? "
                                                "Click 'Cancel' to end the program, "
                                                "click 'No' to come back to the selection window.")
        if res is None:
            logger.debug("Program terminated by the user ('Cancel' button).")
            self.close()
            raise KeyboardInterrupt("Program terminated by the user ('Cancel' button).")
        if res:
            self.close()

    def close(self):
        self.destroy()


class DatePickerTk(MainDateTk):  # obsolete
    def __init__(self, title=None, message=None, default_date=None, dateformat="%Y-%m-%d"):
        super().__init__()
        self.geometry("400x250")
        self.title(title)

        self.main_frame = ttk.Frame(self)
        self.main_frame.pack(expand=True, fill="both", pady=15, padx=15)

        ttk.Label(self.main_frame, justify="left", text=message).grid(row=0, columnspan=2, sticky=W + E)

        self.date_picker = Datepicker(self.main_frame, dateformat=dateformat)
        if default_date is None:
            default_date = datetime.datetime.now()
        if isinstance(default_date, datetime.datetime):
            self.date_picker.current_date = default_date
            self.date_picker.current_text = default_date.strftime(dateformat)
        self.date_picker.grid(row=1, column=0, sticky=W)

        self.button_ok = ttk.Button(self.main_frame, text='OK', command=self.close)
        self.button_ok.grid(row=1, column=1, sticky=W)

        if 'win' not in sys.platform:
            self.style = ttk.Style()
            self.style.theme_use('clam')


def get_user_date(title=None, message=None, default_date=None, dateformat="%Y-%m-%d",
                  bypass_dialog=False, behavior_on_error='ignore'):
    """Main function to get a date from  user."""
    import warnings
    warnings.warn("get_user_date is deprecated. Use simpledialog.askdate instead", DeprecationWarning)
    if bypass_dialog:
        return default_date or datetime.datetime.now()
    if title is None:
        title = "Select a date"
    if message is None:
        message = "Enter the date (ISO format YYYY-MM-DD):"
    m_root = DatePickerTk(title=title, message=message, default_date=default_date, dateformat=dateformat)
    m_root.mainloop()
    date_selected = m_root.date_picker.current_date
    logger.info('Date picked: {}'.format(date_selected))
    if not date_selected:
        msg = 'Wrong date selected. Please try again.'
        raise_anomaly(flag=behavior_on_error, error=ValueError, title=msg, message=msg)
    return date_selected


if __name__ == "__main__":
    print(askdate())
    print(askperiod())
    print(askperiod(choices=[datetime.datetime.now()]))
