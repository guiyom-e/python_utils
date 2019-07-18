# open source
import sys

from tools.logger import logger
from tools.exceptions import UnknownError
from tools.helpers.interface import messagebox


def raise_anomaly(flag="ask", error=None, title=None, message=None, use_messagebox=True):
    """Raise an 'anomaly' depending on the flag argument:
        - 'ignore': do nothing and return,
        - 'warning': show a warning (warning logger and tkinter messagebox),
        - 'error': raises an exception,
        - 'ask': ask the user either to ignore the anomaly or to raise an error.

    :param flag: must be 'ask', 'ignore', 'warning', 'error'
    :param error: Exception
    :param title: Title for message box and logger.
    :param message: Message for message box and error logger.
    :param use_messagebox: if True the tkinter messagebox will be used to show errors.
    :return:
    """
    # Incorrect flag
    if not isinstance(flag, str):
        msg = "Incorrect type '{}' for flag argument which must be a string.".format(type(flag))
        logger.error(msg)
        raise TypeError(msg)

    # Define unknown errors
    if not isinstance(title, str) or message is None:
        title = "Unknown error."
    if not isinstance(message, str) or message is None:
        message = "Unknown error."

    # Ask flag
    if flag == 'ask':
        res = messagebox.askyesnocancel(title=title,
                                        message="{}\n\nDo you want to continue "
                                                "the program otherwise (not recommended)?".format(message),
                                        default='no')
        if res is None:
            logger.debug("Anomaly 'ask' raised with title '{}' "
                         "and message '{}'.".format(title, message))
            logger.info("Program stopped by the user ('Cancel' button).")
            sys.exit(0)
        if res:
            flag = 'ignore'
        else:
            flag = 'error'
            use_messagebox = False  # message has already been shown.

    # Ignore flag
    if flag == 'ignore':
        logger.debug("Anomaly 'ignore' raised with title '{}' and message '{}'.".format(title, message))
        return

    # Warning flag
    if flag == 'warning':
        logger.warning("Anomaly 'warning' raised with title '{} and message '{}'.".format(title, message))
        if use_messagebox:
            messagebox.showwarning(title=title, message=message)
        return

    # Error flag
    if flag == 'error':
        logger.debug("Anomaly 'error' raised with title '{}'.".format(title))
        if not isinstance(error, BaseException):
            error = UnknownError
        if use_messagebox:
            messagebox.showerror(title=title, message=message)
        msg = '{}\n\n{}'.format(title, message)
        logger.error(msg)
        raise error(msg)

    # Unknown flag
    msg = "Incorrect value '{}' for flag argument which must be 'ask', 'ignore', 'warning' or 'error'. " \
          "Original error was: {}\n\n{}".format(flag, title, message)
    logger.error(msg)
    raise ValueError(msg)


def raise_no_file_selected_anomaly(flag, use_messagebox=True):
    """Anomaly if no file selected.

    :param flag: must be 'ask', 'ignore', 'warning', or 'error'
    :param use_messagebox: boolean. if True a messagebox will appear
    :return:
    """
    raise_anomaly(flag,
                  error=FileNotFoundError,
                  title='No file selected!',
                  message='No file has been selected.',
                  use_messagebox=bool(use_messagebox),
                  )


def raise_bad_extension_anomaly(flag, use_messagebox=True, msg=None):
    """Anomaly if bad extension set.

    :param flag: must be 'ask', 'ignore', 'warning', or 'error'
    :param use_messagebox: boolean. if True a messagebox will appear
    :param msg: custom message
    :return:
    """
    raise_anomaly(flag,
                  error=ValueError,
                  title='Bad extension set!',
                  message=msg or 'The selected file has a bad extension. Please try again.',
                  use_messagebox=bool(use_messagebox),
                  )


# For testing purposes
if __name__ == "__main__":
    import logging
    logger.handlers[0].setLevel(logging.DEBUG)
    raise_anomaly(flag="ignore")
    raise_anomaly(flag="warning")
    try:
        raise_anomaly(flag="error")
    except UnknownError:
        pass
    try:
        raise_anomaly(flag=0)
    except TypeError:
        pass
    try:
        raise_anomaly(flag="bobby")
    except ValueError:
        pass
    raise_anomaly(flag="ask")
