from tkinter import ttk, Scrollbar, N, S, E, Text, W, END


class TextFrame(ttk.Frame):
    def __init__(self, master=None, text="", height=600, width=500, **options):
        ttk.Frame.__init__(self, master, height=height, width=width, **options)
        self.grid_propagate(0)

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=0)
        self.rowconfigure(0, weight=1)

        self.scrollbar = Scrollbar(self)
        self.scrollbar.grid(row=0, column=1, sticky=(N, S, E))

        self.text = Text(self, yscrollcommand=self.scrollbar.set)
        self.text.grid(row=0, column=0, sticky=(N, S, E, W))
        if text:
            self.text.config(state='normal')
            self.text.insert(END, text)
            self.text.config(state='disabled')

        self.scrollbar.config(command=self.text.yview)
