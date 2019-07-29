from tkinter import Tk, TclError


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
