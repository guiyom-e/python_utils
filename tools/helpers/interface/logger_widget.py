# -*- coding: utf-8 -*-
# open source project
"""
Defines a text frame updated by a logger handler. Support multi-threading.
"""
import time
import threading
import logging
from tkinter import END, Tk

from tools.logger import logger
from tools.helpers.interface.text_frame import TextFrame


class LoggingHandlerFrame(TextFrame):
    """Text frame updated by a logger handler."""
    class Handler(logging.Handler):
        def __init__(self, widget, level=logging.INFO):
            logging.Handler.__init__(self)
            self.setLevel(level)
            self.setFormatter(logging.Formatter("%(levelname)s: %(message)s"))
            self.widget = widget
            self.widget.config(state='disabled')

        def emit(self, record):
            self.widget.config(state='normal')
            self.widget.insert(END, self.format(record) + "\n")
            self.widget.see(END)
            self.widget.config(state='disabled')

    def __init__(self, master=None, level=logging.INFO, height=200, width=500, **options):
        TextFrame.__init__(self, master, height=height, width=width, **options)
        self.logging_handler = LoggingHandlerFrame.Handler(self.text, level=level)

    def quit(self):
        """Detach logger before closing"""
        self.logging_handler.close()
        logger.removeHandler(self.logging_handler)
        super().quit()


# For testing purposes
if __name__ == '__main__':
    def worker():
        # Skeleton worker function, runs in separate thread (see below)
        while True:
            # Report time / date at 2-second intervals
            time.sleep(2)
            time_str = time.asctime()
            msg = 'Current time: ' + time_str
            logging.info(msg)

    root = Tk()
    frame = LoggingHandlerFrame(root)
    frame.pack()
    t1 = threading.Thread(target=worker, args=[])
    t1.start()
    logger.info('test_a')
    logger.addHandler(frame.logging_handler)
    logger.info('test_b')
    root.mainloop()
    frame.quit()
    logger.info('test_c')
    t1.join()
