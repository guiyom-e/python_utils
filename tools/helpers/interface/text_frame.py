# -*- coding: utf-8 -*-
# open source project
"""
Frame, dialog and Tk window with text in it.
"""
from tkinter import ttk, Scrollbar, N, S, E, Text, W, END, BOTH
from tools.helpers.interface.basics import CustomTk
from tools.helpers.interface.wrappers import frame_integration, dialog_function, CustomDialog


class TextFrame(ttk.Frame):
    """Frame with text in it."""
    def __init__(self, master=None, text="", height=600, width=500, **options):
        super().__init__(master, height=height, width=width, **options)
        self.grid_propagate(0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky=(N, S, E))

        self.text = Text(self, yscrollcommand=self.scrollbar.set)
        self.text.grid(row=0, column=0, sticky=(N, S, E, W))
        text = str(text)
        if text:
            self.text.config(state='normal')
            self.text.insert(END, text)
            self.text.config(state='disabled')

        self.scrollbar.config(command=self.text.yview)


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
def showtext(title: str = None, text: str = None, **options):
    """Show a long text in a dialog"""
    pass


if __name__ == '__main__':
    showtext(text="Hello world!")
