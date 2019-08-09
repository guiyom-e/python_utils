# -*- coding: utf-8 -*-
# open source project
"""
Model classes and basic functions.
"""
import tkinter as tk
from tkinter import Tk, TclError, ttk, N, S, E, W


class CustomTk(Tk):
    def __init__(self, title=None, **options):
        super().__init__(**options)
        try:  # Add icon
            self.iconbitmap('tools/favicon.ico')
        except TclError:
            pass
        self.title('' if title is None else title)
        self.lift()


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


class FrameWithScrollbar(ttk.Frame):
    """Frame with a vertical scrollbar.
    Access to canvas: '.canvas'; access to child frame: '.frame'"""

    def __init__(self, master=None, **options):
        super().__init__(master, **options)

        self.canvas = tk.Canvas(self, borderwidth=0)
        self.frame = ttk.Frame(self.canvas)
        self.vsb = ttk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.canvas.configure(yscrollcommand=self.vsb.set)
        self.vsb.pack(side="right", fill="y")
        self.canvas.pack(side="left", fill="both", expand=True)
        # self.frame.pack(side="left", fill="both", expand=True)
        self.frame.bind("<Configure>", self.on_frame_configure)
        self.canvas.create_window((1, 1), window=self.frame, anchor="nw", tags="self.frame")

    def on_frame_configure(self, _event):
        """Reset the scroll region to encompass the inner frame"""
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
