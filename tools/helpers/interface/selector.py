import tkinter as tk
from tkinter import ttk


class TkSelector(tk.Tk):
    def __init__(self, title: str = "Selection", icon_path: str = 'tools/favicon.ico',
                 selections=None, initial_value="Select an option", **options):
        super().__init__(**options)
        try:  # Add icon
            self.iconbitmap(icon_path)
        except tk.TclError:
            pass
        self.title('' if title is None else title)
        self.var = tk.StringVar(self)
        selections = selections or []
        self.option = ttk.OptionMenu(self, self.var, *selections)
        self.option.pack()
        self.var.set(initial_value)  # initial value
        self.button = ttk.Button(self, text="OK", command=self.destroy)
        self.button.pack()