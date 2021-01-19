# -*- coding: utf-8 -*-
# open source project
"""
Frame, dialog and Tk window with text in it.
"""
from tkinter import ttk, Scrollbar, N, S, E, Text, W, END, BOTH, NONE, CHAR, WORD
from typing import Union

from tools.helpers.interface.basics import CustomTk
from tools.helpers.interface.wrappers import frame_integration, dialog_function, CustomDialog


class TextFrame(ttk.Frame):
    """Frame with text in it."""

    def __init__(self, master=None, text="", height=600, width=500, wrap=CHAR, **options):
        """Display a frame with text.

        :param master: master component
        :param text: text to display
        :param height: height of the text frame
        :param width: width of the text frame
        :param wrap: whether to allow text wrapping. Can be CHAR (default), WORD (or True) or NONE (or False).
        If wrap is NONE (or False), a scrollbar is added on x axis.
        :param options: options to pass to the tkinter Frame
        """
        super().__init__(master, height=height, width=width, **options)
        self.grid_propagate(0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar_y = Scrollbar(self)

        if wrap in (False, None, NONE):
            wrap = NONE
            show_scrollbar_x = True
        else:
            if wrap is True:
                wrap = WORD
            show_scrollbar_x = False

        if show_scrollbar_x:
            self.scrollbar_y.grid(row=0, column=1, rowspan=2, sticky=(N, S, E))
            self.scrollbar_x = Scrollbar(self, orient='horizontal')
            self.scrollbar_x.grid(row=1, column=0, columnspan=2, sticky=(S, E, W))
            self.text = Text(self, yscrollcommand=self.scrollbar_y.set, xscrollcommand=self.scrollbar_x.set, wrap=wrap)
        else:
            self.scrollbar_y.grid(row=0, column=1, sticky=(N, S, E))
            self.text = Text(self, yscrollcommand=self.scrollbar_y.set, wrap=wrap)
        self.text.grid(row=0, column=0, sticky=(N, S, E, W))
        text = str(text)
        if text:
            self.text.config(state='normal')
            self.text.insert(END, text)
            self.text.config(state='disabled')

        self.scrollbar_y.config(command=self.text.yview)
        if show_scrollbar_x:
            self.scrollbar_x.config(command=self.text.xview)


class TextTk(CustomTk):
    """Text window"""

    def __init__(self, title=None, text="", **options):
        title = title or ""
        super().__init__(title=title)
        options.pop('master', None)
        self._frame = TextFrame(master=self, text=text, **options)
        self._frame.pack(fill=BOTH, expand=True)


@frame_integration(TextFrame, okcancel=False)
class TextDialog(CustomDialog):
    """Text frame integrated in a dialog"""
    pass


@dialog_function(TextDialog)
def showtext(title: str = None, text: str = None, wrap: Union[bool, CHAR, WORD, NONE, None] = CHAR, **options):
    """Show a long text in a dialog"""
    pass


if __name__ == '__main__':
    showtext(text="Hello world!")
