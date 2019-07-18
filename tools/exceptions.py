"""
Customized exceptions.
"""


class UnknownError(Exception):
    """Unknown error."""
    pass


class DateError(Exception):
    """Error linked to date."""
    pass


class TooLateDateError(DateError):
    """Date is too late."""
    pass
