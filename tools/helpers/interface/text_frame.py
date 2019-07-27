from tkinter import ttk, Scrollbar, N, S, E, Text, W, END
from tools.helpers.interface.basics import CustomTk, frame_integration, dialog_function


class TextFrame(ttk.Frame):
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


@frame_integration(TextFrame, okcancel=False)
class TextTk(CustomTk):
    pass


@dialog_function(TextTk)
def showtext(title: str = None, text: str = None, **options):
    pass


if __name__ == '__main__':
    showtext(text="Hello world!")
