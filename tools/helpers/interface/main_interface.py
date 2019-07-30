# -*- coding: utf-8 -*-
# open source
"""
Interface with multiple parts containing buttons corresponding to one function each.
Includes a logger frame and a help window.
"""
import logging
import tkinter as tk
from collections import OrderedDict
from tkinter import ttk, TclError
import threading
from queue import Queue, Empty

from tools.logger import logger
from tools.helpers.interface import messagebox, CustomTk
from tools.helpers.interface.custom_messagebox import CustomQuestionFrame
from tools.helpers.interface.logger_widget import LoggingHandlerFrame
from tools.helpers.interface.text_frame import TextTk
from tools.helpers.models import IdentityDict


class _ThreadedTask(threading.Thread):
    """Daemon thread where functions are run."""
    def __init__(self, queue, func, func_name=None, *args, **kwargs):
        threading.Thread.__init__(self, daemon=True)  # daemon: this thread will exit if the main thread exits
        self.queue = queue
        self.func = func
        self.func_name = func_name or func.__name__.replace("_", " ").capitalize()
        self.args = args
        self.kwargs = kwargs

    def run(self):
        logger.debug("start task with func '{}'".format(self.func_name))
        try:
            self.func(*self.args, **self.kwargs)
            msg = "'{}' successfully ended.".format(self.func_name)
            logger.info("Function '{}' successfully ended.\n***************\n".format(self.func_name))
        except Exception as err:
            logger.exception(err)
            msg = "'{}' ended with error.".format(self.func_name)
            logger.error("Function '{}' ended with error.\n***************\n".format(self.func_name))
        self.queue.put(msg)  # add func name to queue to indicate that the task is finished
        logger.debug("end task with func '{}'".format(self.func_name))


class _MainPart(ttk.LabelFrame):
    def __init__(self, master: 'MainTk', text, answers, labelanchor='n',
                 geometry_manager='pack', geometry_options=None):
        """Main part of the MainTk window. Should not be instantiated outside a MainTk window.

        :param answers: list of functions or list of tuples withe the format [(function_name, function, tooltip), ...]
        """
        super().__init__(master, text=text, labelanchor=labelanchor)
        self.master = master
        answers = self._format_answers(answers)
        logger.debug("Possible functions: {}".format(answers))
        self.question_frame = CustomQuestionFrame(master=self, choices=answers, auto_quit=False,
                                                  geometry_manager=geometry_manager, geometry_options=geometry_options)
        self.question_frame.pack(fill=tk.BOTH)
        self.question_frame.change_res.trace(mode='w', callback=self.exec_func)  # exec func on click
        self.queue = None

    @staticmethod
    def _format_answers(answers):
        # auto-generate a pretty function name
        func_dict = IdentityDict(func=lambda x: str(x.__name__).replace('_', ' ').capitalize())
        # auto-generate a tooltip from the first line of the docstring
        tooltip_dict = IdentityDict(func=lambda x: str(x.__doc__ or "").split('\n\n')[0])
        n_answers = []
        for ans in answers:
            if isinstance(ans, tuple):
                if len(ans) == 0:  # None
                    n_answers.append(('None', None))
                elif len(ans) == 1:  # function
                    n_answers.append((func_dict[ans], ans[0], tooltip_dict[ans]))
                elif len(ans) == 2:  # name + function
                    n_answers.append((*ans[:2], tooltip_dict[ans[1]]))
                else:
                    n_answers.append(ans)
            else:
                n_answers.append((func_dict[ans], ans, tooltip_dict[ans]))
        return n_answers

    def exec_func(self, _varname, _elementname, _mode):
        # logger.debug("varname, elementname, mode: {}, {}, {}".format(_varname, _elementname, _mode))
        func = self.question_frame.result
        func_name = self.question_frame.result_str
        if func:
            logger.info("***************\nStarting function '{}'...".format(func_name))
            self.master.progressbar.grid(row=0, column=1)
            self.master.progressbar.start(interval=100)
            self.master.func_text.set("{} processing...".format(func_name))
            self.master.disable_all()
            self.queue = Queue()
            self.master.active_thread = _ThreadedTask(self.queue, func, func_name)  # run thread
            self.master.active_thread.start()
            self.master.after(100, self.process_queue)  # check the end of the process every 100 ms

    def process_queue(self):
        try:
            msg = self.queue.get(0)  # check if the process has ended
            # If the process has ended, stop progressbar and activate buttons
            self.master.activate_all()
            self.master.progressbar.stop()
            self.master.progressbar.grid_forget()
            self.master.func_text.set(msg)
        except Empty:  # if the process has not ended, wait again
            self.master.after(100, self.process_queue)


class MainTk(CustomTk):
    """Main Tk window"""
    def __init__(self, parts: OrderedDict, logger_level=logging.INFO,
                 nb_columns=3, help_msg="No help_msg available.", title="main", **options):
        super().__init__(title=title, **options)
        self.help_text = help_msg
        self.help_win = None
        self.load_help()
        self.bind('<F1>', func=self.open_help)
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.parts = OrderedDict()
        for i, (title, answers) in enumerate(parts.items()):
            q_f = _MainPart(master=self, text=title, answers=answers,
                            geometry_manager='grid', geometry_options=dict(sticky='ew', nb_columns=nb_columns))
            q_f.pack(fill=tk.BOTH)
            self.parts[title] = q_f
        # Info frame
        self.info_frame = ttk.Frame(master=self)
        self.info_frame.pack(fill=tk.BOTH, expand=True)
        self.func_text = tk.StringVar()
        self.func_label = ttk.Label(master=self.info_frame, textvariable=self.func_text)
        self.func_label.grid(row=0, column=0, sticky=tk.W)
        self.progressbar = ttk.Progressbar(master=self.info_frame, mode='indeterminate', length=200, value=0)
        self.help_button = ttk.Button(master=self.info_frame, text="Help", command=self.open_help)
        self.help_button.grid(row=0, column=2, sticky='e')
        self.logger_frame = LoggingHandlerFrame(master=self.info_frame, level=logger_level)
        self.logger_frame.grid(row=1, column=0, columnspan=3, sticky='nsew')
        self.info_frame.grid_rowconfigure(1, weight=1)  # make logger frame expandable vertically
        self.info_frame.grid_columnconfigure(0, weight=1)  # idem horizontally
        self.active_thread = None
        logger.addHandler(self.logger_frame.logging_handler)
        logger.debug("Window loaded.")
        logger.info("Main window loaded. Please select an option or quit.")

    @staticmethod
    def ask_exit(name='unknown'):
        msg = "The function '{}' is running in background, are you sure you want to exit the program now?".format(name)
        res = messagebox.askyesno(title="Process running in background!", message=msg, default='no')
        return res

    def on_closing(self):
        # Case of an active thread
        if self.active_thread and self.active_thread.is_alive():
            logger.warning("Process running in background!")
            logger.debug("Thread '{}: {}' still alive.".format(self.active_thread.name, self.active_thread))
            logger.debug("number of active threads: {}, current thread: {}, main thread: {}."
                         .format(threading.active_count(), threading.current_thread(), threading.main_thread()))
            self.active_thread.join(timeout=1)  # wait 1 second
            if self.active_thread.is_alive():  # if the thread is still alive after 1 second
                if not self.ask_exit(self.active_thread.func_name):
                    logger.debug("Exit cancelled")
                    return False
        # Remove logger handler attached to tkinter frame
        self.logger_frame.quit()
        # Destroy the window
        self.destroy()
        logger.debug("Main window destroyed.")
        self.quit()
        logger.debug("Main window quited.")
        return True

    def activate_all(self):
        for _name, part in self.parts.items():
            for button in part.question_frame.options:
                button['state'] = tk.NORMAL

    def disable_all(self):
        for _name, part in self.parts.items():
            for button in part.question_frame.options:
                button['state'] = tk.DISABLED

    def load_help(self):
        self.help_win = TextTk(title="Help", text=self.help_text, height=600, width=800)
        self.help_win.withdraw()
        self.bind('<F1>', func=self.open_help)

    def open_help(self, _event=None):
        exists = False
        try:
            if self.help_win.winfo_exists():
                exists = True
        except TclError:
            pass
        if not exists:
            self.load_help()
            self.help_win.bind('<Control-F1>', func=self.__easter_egg)
        self.help_win.deiconify()
        self.help_win.mainloop()
        self.help_win.quit()

    def __easter_egg(self, *_args, **_kwargs):
        if not hasattr(self, '_cntpwin'):
            self._cntpwin = 1
        else:
            self._cntpwin += 1
        eastr = b"                                                                               \n                           .\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xc3\xa6\xc3\xa6\xe2\x95\x90\xe2\x89\xa4BB\xe2\x95\x9cB\xc2\xa5\xc2\xa5\xc2\xa5\xc2\xa5\xc2\xa5\xc2\xa5\xe2\x96\x80\xc2\xaaBBRR\xc2\xa5\xe2\x95\x90\xe2\x95\x90\xe2\x95\x90\xe2\x89\xa4\xc3\xa6\xe2\x96\x84                      \n                    .\xe2\x96\x84\xe2\x89\xa4\xe2\x95\x9c\xe2\x95\xa9\xe2\x95\x99\xe2\x95\x99\xe2\x96\x80^            \xc2\xa1\xc2\xa1      -.       \xe2\x95\x99\xe2\x96\x93,                   \n                 \xe2\x96\x84\xe2\x96\x93\xe2\x96\x80.                   . \xc2\xac ..        .     \xe2\x96\x80\xe2\x96\x84                  \n                \xe2\x96\x88\xe2\x95\x99                                `          \xe2\x95\x99\xe2\x96\x8c                 \n               \xe2\x94\x8c\xe2\x96\x88              (           .\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84,    `      \xe2\x95\x99\xe2\x96\x8c                \n             \xe2\x95\x93\xe2\x96\x93\xe2\x96\x80       \xe2\x96\x84\xe2\x96\x93\xe2\x95\xa9\xe2\x96\x80\xe2\x96\x93\xe2\x96\x93\xe2\x96\x84\xe2\x96\x84         \xe2\x96\x84\xe2\x96\x93\xe2\x96\x80\xe2\x94\x94 \xe2\x96\x80\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x96\x84        ..\xe2\x96\x84\xe2\x96\x80\xe2\x96\x84              \n            \xe2\x96\x93\xe2\x95\x99 \xe2\x94\x80       \xe2\x95\x99\xe2\x95\x99\xe2\x95\x99\xe2\x95\x99\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x88\xe2\x96\x93\xce\xa6\xe2\x94\x80    \xe2\x96\x80\xe2\x96\x88\xe2\x96\x84#\xe2\x96\x80\xe2\x96\x80\xe2\x95\x99\xe2\x94\x94\xe2\x96\x84\xe2\x94\x94\xe2\x94\x94\xe2\x94\x94\xe2\x95\x99\xe2\x96\x80 ^\xc2\xac .\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xc2\xbf  `w\xe2\x96\x80\xe2\x95\x97,           \n           \xe2\x96\x88 / \xc2\xba \xe2\x96\x84\xe2\x89\xa4\xc2\xa5\xc3\xa6\xe2\x96\x84         \xe2\x96\x90b               \xe2\x96\x80\xc2\xa5\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84R\xe2\x96\x80\xe2\x95\x99 \xe2\x96\x84  \xe2\x95\x99\xe2\x96\x80\xe2\x96\x84  ,\xe2\x95\x99\xe2\x96\x93          \n           \xe2\x96\x88 \xe2\x95\x90 \xe2\x94\x80   \xe2\x94\x8c\xe2\x96\x84 \xe2\x96\x80\xe2\x96\x80\xe2\x95\x9c=   .\xc3\xa6\xe2\x96\x80                        .\xe2\x96\x84\xe2\x96\x93\xe2\x96\x88\xe2\x96\x84   \xe2\x96\x88  % \xe2\x96\x90\xe2\x96\x84         \n            \xe2\x96\x80\xe2\x89\xa1 `  \xe2\x94\x8c\xe2\x96\x88\xe2\x96\x88     .\xc3\xa6\xe2\x96\x88\xe2\x96\x88       .. .\xc2\xac\xe2\x96\x80b''''`  \xe2\x96\x84\xe2\x96\x84\xe2\x96\x93\xe2\x96\x93\xe2\x96\x80\xe2\x95\x99  \xe2\x96\x93\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80 \xe2\x96\x88  \xe2\x94\x80 \xe2\x95\xab\xe2\x95\x90         \n             \xe2\x96\x88\xc2\xac   \xe2\x96\x88\xe2\x96\x80\xe2\x96\x88\xe2\x96\x93\xe2\x96\x84       \xe2\x96\x80\xe2\x96\x84 \xe2\x95\x93  \xe2\x94\x94  .\xc2\xac-\xe2\x96\x80  \xe2\x96\x84\xe2\x96\x84\xe2\x96\x93\xe2\x96\x93\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x88\xe2\x96\x8c   \xe2\x96\x84\xe2\x96\x88\xe2\x96\x88        \xe2\x96\x93\xe2\x96\x80          \n              \xe2\x96\x88  \xe2\x96\x90\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x96\x90\xe2\x96\x88\xe2\x96\x80\xe2\x96\x93\xe2\x96\x93\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84.  \xe2\x96\x84\xe2\x96\x84.\xc2\xbf\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xc3\xa6\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x88\xc2\xac    .\xe2\x96\x84\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x96\x80\xe2\x96\x88\xe2\x96\x80      \xe2\x8c\x90\xe2\x96\x93\xe2\x96\x80            \n              \xe2\x96\x90\xe2\x96\x84 \xe2\x96\x90\xe2\x96\x88\xe2\x96\x88\xe2\x96\x84\xe2\x96\x88\xe2\x96\x8c \xe2\x96\x90\xe2\x96\x88 .\xe2\x94\x94\xe2\x94\x94\xe2\x96\x90\xe2\x96\x88\xe2\x94\x94\xe2\x94\x94\xe2\x94\x94.\xe2\x96\x88\xe2\x95\x90      \xe2\x96\x88\xe2\x96\x84\xe2\x96\x93\xe2\x96\x93\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x96\x88\xe2\x96\x80 \xe2\x96\x84\xe2\x96\x80       \xe2\x96\x84\xe2\x96\x80              \n              j\xe2\x96\x8c  \xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x88\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x88\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x95\x99\xc2\xac   \xe2\x96\x80\xe2\x96\x88\xe2\x96\x88\xc2\xac       \xe2\x96\x93\xe2\x95\x90               \n              \xe2\x96\x90b  \xe2\x96\x80\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x88\xe2\x96\x80\xe2\x95\x99\xe2\x94\x94  \xe2\x94\x94\xe2\x96\x88,   .\xe2\x96\x84\xe2\x96\x80\xe2\x95\x99        \xe2\x96\x93\xc2\xac                \n              \xe2\x95\xab    \xe2\x96\x88\xe2\x96\x8c\xe2\x96\x88\xe2\x94\x80\xe2\x96\x80\xe2\x96\x88 \xe2\x95\x9d\xe2\x96\x88\xc2\xac .\xe2\x96\x88\xe2\x96\x8c    \xe2\x96\x88\xe2\x96\x8c      \xe2\x96\x90\xe2\x96\x88\xc3\xa6\xc3\xaa\xe2\x96\x80.         \xe2\x96\x84\xe2\x96\x80                  \n              \xe2\x96\x88     \xe2\x94\x94\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x88\xe2\x96\x8c\xe2\x96\x84\xe2\x96\x88\xe2\x96\x88\xe2\x96\x84 \xe2\x96\x90\xe2\x96\x88\xe2\x96\x84..\xe2\x96\x84\xe2\x96\x88\xe2\x96\x8c\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xce\xa6\xe2\x96\x80\xe2\x96\x80\xe2\x95\x99      .    \xe2\x96\x84\xe2\x95\x9d\xe2\x96\x80                    \n              \xe2\x96\x8c             .\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x8c\x90       .  \xe2\x8c\x90\xe2\x94\x80   .\xe2\x96\x84#\xe2\x96\x80\xe2\x94\x94                       \n             j\xe2\x96\x8c        ` \xe2\x94\x80\xc2\xac\xc2\xac\xe2\x8c\x90\xe2\x8c\x90\xe2\x8c\x90\xe2\x8c\x90\xe2\x8c\x90\xc2\xac\xc2\xac\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80 ^[\xe2\x8c\x90\xe2\x94\x80^    \xe2\x96\x84\xc3\xa6\xe2\x95\x9c\xe2\x95\x99\xc2\xac                           \n              \xe2\x96\x88         *\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80\xe2\x94\x80 ^         \xe2\x96\x84#\xe2\x96\x80\xe2\x94\x94                                \n               \xe2\x96\x80\xe2\x96\x84                  \xe2\x96\x84\xe2\x96\x84\xe2\x96\x93\xe2\x96\x93\xe2\x96\x93\xc2\xa5R\xe2\x96\x80\xe2\x94\x94                                    \n                 \xe2\x94\x94\xe2\x96\x80%\xc3\xa6\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xe2\x96\x84\xc3\xa6\xc3\xa6\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x96\x80\xe2\x95\x99.                                           \n                                                                               "
        text = "Number of windows opened: {}\n\n".format(self._cntpwin) + eastr.decode()
        messagebox.showtext(title="Looking for some more help??", text=text, height=500, width=700)
