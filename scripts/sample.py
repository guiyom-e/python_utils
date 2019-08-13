import os

from tools.logger import logger
from tools.helpers.interface import messagebox, simpledialog


def try_it():
    """Try something! (this message is shown by default as tooltip)"""
    # Test logger
    logger.debug('Test debug message')
    logger.info('Test info message')
    logger.error('Test error message')

    # Print directories
    logger.info("Working directory: {}".format(os.getcwd()))
    logger.info("File path: {}".format(__file__))

    # Test message box
    res = messagebox.askyesno(title="This is a message box!", message="Do you want to raise an error?")
    if res:
        err_msg = "This is the error you asked!"
        logger.error(err_msg)
        raise ValueError(err_msg)
    logger.info("No error was raised!")

    # Test get_user_date
    message = "This is the end of this sample script ending at {}".format(simpledialog.askdate(bypass_dialog=True))
    messagebox.showinfo(title="This is already the end...", message=message)


if __name__ == '__main__':
    try_it()
