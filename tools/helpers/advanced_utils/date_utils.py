# -*- coding: utf-8 -*-
# open source project
"""
Utils to manipulate dates:
- reset time of a date
- add a period of time to a date
- get the first date of a period
- get the number of periods separating two dates
- get dates of a specified period
- get a list of multiple periods
- support of datetime objects, pandas timestamps, series and dataframes (most cases)
"""
import datetime
from typing import Union
import pandas as pd
import numpy as np

from tools.helpers.interface import simpledialog
from tools.helpers.utils.decorators import handle_datetime_dataframe, handle_datetime_pandas_objects

STRFTIME_DICT = {'year': "%Y", "month": "%Y-%m", "quarter": "%Y-%m",
                 "week": "%Y-W%W",  # WARN: week format don't respect ISO 8601 here
                 "day": "%Y-%m-%d", None: "%Y-%m-%d",
                 "hour": "%H:%M", "minute": "%H:%M", "second": "%H:%M:%S"}

# todo: integrate pandas.date_range

# Reset time
@handle_datetime_dataframe
def reset_timing(date: Union[pd.DataFrame, pd.Series, datetime.datetime],
                 inplace=False) -> Union[pd.DataFrame, pd.Series, datetime.datetime]:
    """Set time to 00:00:00"""
    if isinstance(date, pd.Series):
        date = pd.to_datetime(date)
        return pd.to_datetime(date.dt.date)
    return pd.to_datetime(date.date()) if date is not None else None


# Get quarter
@handle_datetime_dataframe
def get_quarter(date: datetime.datetime, inplace=False):
    """Returns the quarter of a date

    # >>> get_quarter = handle_datetime_dataframe(get_quarter)  # apply decorator for doctest
    >>> date = datetime.datetime(2019, 4, 5, 8, 2, 3)
    >>> get_quarter(date)
    2

    >>> date = pd.Series([datetime.datetime(2019, 1, 5, 8, 2, 3)])
    >>> get_quarter(date)
    0    1
    dtype: int64

    >>> date = pd.DataFrame(data=[datetime.datetime(2019, 12, 5, 8, 2, 3)])
    >>> get_quarter(date)
       0
    0  4
    >>> get_quarter(date, inplace=True)
    >>> date
       0
    0  4
    """
    if isinstance(date, pd.Series):
        date = pd.to_datetime(date)
        return (pd.to_datetime(date).dt.month - 1) // 3 + 1
    return (date.month - 1) // 3 + 1


# Add periods
@handle_datetime_pandas_objects
def add_period(date: Union[pd.DataFrame, pd.Series, datetime.datetime, None], number_of_period=0,
               period_type=None, reset_time=False, output_type=pd.Timestamp, inplace=False, **kwargs):
    """Add a certain number of periods (year, month, week, day, hour, minute, second) to the input date.

    >>> add_period = handle_datetime_pandas_objects(add_period)  # apply decorator for doctest
    >>> date = datetime.datetime(2019, 1, 5, 8, 2, 3)
    >>> add_period(date, 2, period_type='week', reset_time=True)
    Timestamp('2019-01-19 00:00:00')

    >>> date = pd.Series([datetime.datetime(2019, 1, 5, 8, 2, 3)])
    >>> add_period(date, 3, period_type='week', reset_time=True)
    0   2019-01-26
    dtype: datetime64[ns]

    >>> date = pd.DataFrame(data=[datetime.datetime(2019, 1, 5, 8, 2, 3)])
    >>> add_period(date, 4, period_type='week', reset_time=True)
               0
    0 2019-02-02
    >>> add_period(None, 4, period_type='week', reset_time=True)
    NaT

    :param date: initial date
    :param number_of_period: number of periods to add
    :param period_type: one of: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'.
    :param reset_time: if True, time is reset to 00:00:00.
    :param output_type: type of the output / function to apply to the output. pd.Timestamp by default.
    :param inplace: if date is a dataframe and inplace is True, convert columns inplace
    :param kwargs: keyword arguments (unused)
    :return: date of type output_type
    """
    date = pd.to_datetime(date)
    if period_type is None:
        n_date = date
    elif period_type == 'year':
        n_year = date.year + number_of_period
        n_date = date.replace(year=n_year)
    elif period_type == 'month':
        n_year = date.year + (date.month + number_of_period - 1) // 12
        n_month = (date.month + number_of_period) % 12 or 12
        n_date = date.replace(month=n_month)
        n_date = n_date.replace(year=n_year)
    elif period_type == 'quarter':
        return add_period(date, number_of_period=3 * number_of_period, period_type='month',
                          reset_time=reset_time, output_type=output_type, **kwargs)
    elif period_type == 'week':
        n_date = date + pd.Timedelta(weeks=number_of_period)
    elif period_type == 'day':
        n_date = date + pd.Timedelta(days=number_of_period)
    elif period_type == 'hour':
        n_date = date + pd.Timedelta(hours=number_of_period)
    elif period_type == 'minute':
        n_date = date + pd.Timedelta(minutes=number_of_period)
    elif period_type == 'second':
        n_date = date + pd.Timedelta(seconds=number_of_period)
    else:
        raise NotImplementedError("period_type '{}' not valid!".format(period_type))
    n_date = reset_timing(n_date) if reset_time else n_date
    return output_type(n_date)


def add_month(date, number_of_months=0, reset_time=False, output_type=pd.Timestamp, **kwargs):
    """Add number_of_months months to date. number_of_months can be negative or positive."""
    return add_period(date, number_of_months, period_type='month',
                      reset_time=reset_time, output_type=output_type, **kwargs)


def add_week(date, number_of_weeks=0, reset_time=False, output_type=pd.Timestamp, **kwargs):
    """Add number_of_weeks weeks to date. number_of_months can be negative or positive.
    Monday is the first day of week (following ISO 8601)."""
    return add_period(date, number_of_weeks, period_type='week',
                      reset_time=reset_time, output_type=output_type, **kwargs)


# Get first date of a period
@handle_datetime_pandas_objects
def reset_period(date: Union[pd.DataFrame, pd.Series, datetime.datetime, None],
                 period_type: str, offset: int = 0, reset_time=True,
                 inplace=False) -> Union[pd.DataFrame, pd.Series, datetime.datetime, None]:
    """Get the first day of the period of 'date' with an offset of 'offset' period(s).
    Monday is the first day of week (following ISO 8601).

    :param date: selected date in the week.
    :param period_type:  one of: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'.
    :param offset: add or remove a certain number of periods. Default: 0.
    :param reset_time: if True, time (hours, minutes, seconds, milliseconds) are set to 00:00:00
    :param inplace: if date is a dataframe and inplace is True, convert columns inplace
    :return: first day in the period of 'date' (pd.TimeStamp object).
    """
    if date is None or date is pd.NaT:
        return date
    date = pd.to_datetime(date)
    n_date = add_period(date, offset, period_type=period_type)
    if period_type == 'year':
        n_date = n_date.replace(month=1, day=1)
    elif period_type == 'quarter':
        n_date = n_date.replace(month=3 * ((n_date.month - 1) // 3) + 1, day=1)
    elif period_type == 'month':
        n_date = n_date.replace(day=1)
    elif period_type == 'day':
        n_date = reset_timing(n_date)
    elif period_type == 'hour':
        n_date = n_date.replace(minute=1, second=0, microsecond=0)
    elif period_type == 'minute':
        n_date = n_date.replace(second=0, microsecond=0)
    elif period_type == 'second':
        n_date = n_date.replace(microsecond=0)
    elif period_type == 'week':
        n_date -= pd.Timedelta(days=n_date.weekday())
    else:
        raise NotImplementedError("period_type '{}' not implemented".format(period_type))
    n_date = reset_timing(n_date) if reset_time else n_date
    return n_date


def reset_week(date: datetime.datetime, week_offset: int = 0, reset_time=True) -> datetime.datetime:
    """Get the first day of the week of 'date' with an offset of 'week_offset' week(s).
    Monday is the first day of week (following ISO 8601).

    >>> date_1 = datetime.datetime(2017, 12, 20)  # support of datetime.datetime
    >>> reset_week(date_1, week_offset=0)
    Timestamp('2017-12-18 00:00:00')
    >>> date_2 = datetime.datetime(2017, 12, 20, 23, 54, 59, 92584)
    >>> reset_week(date_2, week_offset=+8)
    Timestamp('2018-02-12 00:00:00')
    >>> reset_week(date_2, week_offset=+8, reset_time=False)
    Timestamp('2018-02-12 23:54:59.092584')
    >>> date_3 = pd.Timestamp(2017, 12, 20)  # support of pandas TimeStamp
    >>> first_day = reset_week(date_3, week_offset=-1)
    >>> first_day
    Timestamp('2017-12-11 00:00:00')
    >>> isinstance(first_day, datetime.datetime)
    True
    >>> isinstance(first_day, pd.Timestamp)
    True

    :param date: selected date in the week.
    :param week_offset: add or remove a certain number of weeks. Default: 0.
    :param reset_time: if True, time (hours, minutes, seconds, milliseconds) are set to 00:00:00
    :return: first day in the week of 'date' (pd.TimeStamp object).
    """
    return reset_period(date, period_type='week', offset=week_offset, reset_time=reset_time)


def reset_month(date: datetime.datetime, month_offset: int = 0, reset_time=True) -> datetime.datetime:
    """Get the first day of the month of 'date' with an offset of 'month_offset' month(s).

    >>> date_1 = datetime.datetime(2017, 12, 20)  # support of datetime.datetime
    >>> reset_month(date_1)
    Timestamp('2017-12-01 00:00:00')
    >>> date_2 = datetime.datetime(2017, 12, 20, 23, 54, 59, 92584)
    >>> reset_month(date_2, month_offset=1)
    Timestamp('2018-01-01 00:00:00')
    >>> reset_month(date_2, month_offset=1, reset_time=False)
    Timestamp('2018-01-01 23:54:59.092584')
    >>> date_3 = pd.Timestamp(2017, 12, 20)  # support of pandas TimeStamp
    >>> first_day = reset_month(date_3, month_offset=-12)
    >>> first_day
    Timestamp('2016-12-01 00:00:00')
    >>> isinstance(first_day, datetime.datetime)
    True
    >>> isinstance(first_day, pd.Timestamp)
    True

    :param date: selected date in the month.
    :param month_offset: add or remove a certain number of months. Default: 0.
    :param reset_time: if True, time (hours, minutes, seconds, milliseconds) are set to 00:00:00
    :return: first day in the month of 'date' (pd.TimeStamp object).
    """
    return reset_period(date, period_type='month', offset=month_offset, reset_time=reset_time)


# Datetime deltas
def datetime_delta(date_1: Union[pd.DataFrame, pd.Series, datetime.datetime, None], date_2,
                   period_type='day', abs_val=False):
    """Get the number of periods separating date_1 from date_2.
    Monday is the first day of week (following ISO 8601).

    >>> d1 = datetime.datetime(2018, 12, 30)
    >>> d2 = datetime.datetime(2018, 12, 31)
    >>> d3 = datetime.datetime(2019, 1, 1)
    >>> d4 = datetime.datetime(2019, 1, 14)
    >>> datetime_delta(d1, d2, period_type='week')  # difference of less than 7 days but different week
    1
    >>> datetime_delta(d2, d1, period_type='week')  # the contrary
    -1
    >>> datetime_delta(d2, d3, period_type='week')  # different year but same week (ISO 8601)
    0
    >>> datetime_delta(d3, d4, period_type='week')  # difference of 13 days, but 2 weeks of difference
    2
    >>> datetime_delta(d4, d3, period_type='week')  # the contrary
    -2
    >>> df1 = pd.DataFrame(columns=['a'], data=[[datetime.datetime(2019, 1, 8)]])
    >>> df2 = pd.DataFrame(columns=['b'], data=[[datetime.datetime(2018, 3, 4)]])
    >>> datetime_delta(df1, d1, period_type='month')
       2018-12-30 00:00:00 - a
    0                       -1
    >>> datetime_delta(df1['a'], df2['b'], period_type='year')
    0   -1
    dtype: int64
    >>> datetime_delta(df1, df2, period_type='month')
       b - a
    0    -10


    :param date_1: first date
    :param date_2: second date. if date_2 >= date_1 then output >=0
    :param period_type: one of: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'.
    :param abs_val: if True, output is an absolute value
    :return: number of periods between date_1 and date_2 (subtraction)
    """
    # Handle pandas dataframe type
    if isinstance(date_1, pd.DataFrame) and isinstance(date_2, pd.DataFrame):
        df = pd.DataFrame()
        for col1, col2 in zip(date_1.columns, date_2.columns):
            df[" - ".join([str(col2), str(col1)])] = datetime_delta(date_1[col1], date_2[col2],
                                                                    period_type=period_type, abs_val=abs_val)
        return df
    if isinstance(date_1, pd.DataFrame):
        df = pd.DataFrame()
        for col1 in date_1.columns:
            df[" - ".join([str(date_2), str(col1)])] = datetime_delta(date_1[col1], date_2,
                                                                      period_type=period_type, abs_val=abs_val)
        return df
    if isinstance(date_2, pd.DataFrame):
        df = pd.DataFrame()
        for col2 in date_2.columns:
            df[" - ".join([str(col2), str(date_1)])] = datetime_delta(date_1, date_2[col2],
                                                                      period_type=period_type, abs_val=abs_val)
        return df
    # Handle pandas serie type
    if isinstance(date_1, pd.Series) and isinstance(date_2, pd.Series):
        ls = []
        for ele1, ele2 in zip(date_1, date_2):
            ls.append(datetime_delta(ele1, ele2, period_type=period_type, abs_val=abs_val))
        return pd.Series(ls)
    if isinstance(date_1, pd.Series):
        return date_1.apply(lambda x: datetime_delta(x, date_2, period_type=period_type, abs_val=abs_val))
    if isinstance(date_2, pd.Series):
        return date_2.apply(lambda x: datetime_delta(date_1, x, period_type=period_type, abs_val=abs_val))
    # Calculate datetime deltas
    if date_1 is None or date_2 is None:
        return np.nan
    date_1 = pd.to_datetime(date_1)
    date_2 = pd.to_datetime(date_2)
    if period_type == "year":
        res = date_2.year - date_1.year
    elif period_type == 'quarter':
        diff = 4 * (date_2.year - date_1.year)
        q1, q2 = get_quarter(date_1), get_quarter(date_2)
        diff2 = q2 - q1
        res = diff + diff2
    elif period_type == 'month':
        res = 12 * (date_2.year - date_1.year) + (date_2.month - date_1.month)
    elif period_type == 'week':  # ISO 8601
        # res = 53 * (date_2.isocalendar()[0] - date_1.isocalendar()[0]) + (date_2.week - date_1.week)  # 52 or 53: No!
        diff = (date_2 - date_1).days // 7
        mod = (date_2 - date_1).days % 7
        if date_1 > date_2:  # symmetrical role of date_1 and date_2
            diff += 1
            mod -= 7
        # date_1 + datetime.timedelta(diff*7 + mod) == date_2 should be True
        date_2_mod = date_1 + datetime.timedelta(days=mod)
        res = diff \
              - int(date_1.isocalendar()[:2] > date_2_mod.isocalendar()[:2]) \
              + int(date_1.isocalendar()[:2] < date_2_mod.isocalendar()[:2])
    elif period_type == 'day':
        res = (date_2 - date_1).days
    elif period_type == 'hour':
        res = (date_2 - date_1).seconds * 3600
    elif period_type == 'minute':
        res = (date_2 - date_1).seconds * 60
    elif period_type == 'second':
        res = (date_2 - date_1).seconds
    else:
        raise NotImplementedError(period_type)
    return abs(res) if abs_val else res


def month_delta(date_1, date_2, abs_val=False):
    return datetime_delta(date_1, date_2, abs_val=abs_val, period_type="month")


def week_delta(date_1, date_2, abs_val=False):
    """Get the number of weeks separating date_1 from date_2.
    Monday is the first day of week (following ISO 8601)."""
    return datetime_delta(date_1, date_2, abs_val=abs_val, period_type="week")


# Get period(s)
def get_period(nb_period=1, period_type='week', date_start=None, date_end=None,
               first_day_of_period=True, reset_time=True, **askdate_kwargs):
    """
    >>> get_period(period_type='week', date_start='ask', first_day_of_period=True, \
    default_date=datetime.datetime(2018, 5, 2, 8, 2, 1), bypass_dialog=True)
    (Timestamp('2018-04-30 00:00:00'), Timestamp('2018-05-07 00:00:00'))

    >>> get_period(period_type='month', date_start='ask', first_day_of_period=True, \
    default_date=datetime.datetime(2018, 5, 2, 8, 2, 1), bypass_dialog=True)
    (Timestamp('2018-05-01 00:00:00'), Timestamp('2018-06-01 00:00:00'))

    >>> get_period(period_type='month', date_start=pd.Series([datetime.datetime(2019, 1, 7)]), first_day_of_period=True)

    >>> get_period(period_type='month', date_start=pd.DataFrame(data=[datetime.datetime(2019, 1, 7)]), first_day_of_period=True)


    :param nb_period: number of periods
    :param period_type: week or month
    :param date_start: first day of the period.
                       If None, use date_end to compute date_start.
                       If date_start and date_end are None, return None, None
                       If 'ask', ask the user
    :param date_end: last day of the period.
                       If None, use date_start to compute date_end.
                       If date_start and date_end are None, return None, None
                       If 'ask', ask the user
                       If 'latest', 'today' or 'now', use today date as date_end
    :param first_day_of_period: if True, the first days of the periods are used for date_start and date_end
    :param reset_time: if True, all times are reset to 00:00:00
    :param askdate_kwargs: keyword arguments for simpledialog.askdate function (in case of use)
    :return: date_start, date_end
    """
    title_1 = askdate_kwargs.pop('title', None)
    if isinstance(date_start, str) and date_start in ['ask']:
        title = title_1 or "Start date"
        date_start = simpledialog.askdate(title, **askdate_kwargs)
    if isinstance(date_end, str) and date_end in ['ask']:
        title = title_1 or "End date"
        date_end = simpledialog.askdate(title, **askdate_kwargs)
    elif isinstance(date_end, str) and date_end in ['latest', 'today', 'now']:
        date_end = datetime.datetime.now()
    date_start = reset_timing(date_start) if reset_time else date_start
    date_start = reset_period(date_start, period_type=period_type) if first_day_of_period else date_start
    date_end = reset_timing(date_end) if reset_time else date_end
    date_end = reset_period(date_end, period_type=period_type) if first_day_of_period else date_end
    if date_start is not None and date_end is None:
        date_end = add_period(date_start, nb_period, period_type=period_type)
    elif date_end is not None and date_start is None:
        date_start = add_period(date_end, - nb_period, period_type=period_type)
    return date_start, date_end


def get_periods(date_start=None, date_end=None, nb_period=None, period_type=None, reset_periods=True):
    """Get a list of nb_period periods from date_start and/or to date_end.
    Monday is the first day of week (following ISO 8601).

    >>> from datetime import datetime as dt
    >>> get_periods(date_end = dt(2019, 2, 5), nb_period=1, period_type='week')
    [(Timestamp('2019-01-28 00:00:00'), Timestamp('2019-02-04 00:00:00'))]
    >>> get_periods(date_end = dt(2019, 2, 5), nb_period=1, period_type='week', reset_periods=False)
    [(Timestamp('2019-01-29 00:00:00'), Timestamp('2019-02-05 00:00:00'))]
    >>> get_periods(date_start = dt(2019, 2, 3), date_end = dt(2019, 2, 5))
    [(Timestamp('2019-02-03 00:00:00'), Timestamp('2019-02-05 00:00:00'))]
    >>> get_periods(date_start = dt(2018, 3, 1), date_end = dt(2018, 5, 1), period_type='month')  # None nb_period: auto
    [(Timestamp('2018-03-01 00:00:00'), Timestamp('2018-04-01 00:00:00')), (Timestamp('2018-04-01 00:00:00'), Timestamp('2018-05-01 00:00:00'))]
    >>> get_periods(date_start = dt(2018, 3, 1), date_end = dt(2018, 5, 1), period_type='month', nb_period=1)
    [(Timestamp('2018-03-01 00:00:00'), Timestamp('2018-04-01 00:00:00'))]

    :param date_start: minimum date
    :param date_end: maximum date
    :param nb_period: number of periods. If None, nb_period is set to 1 if date_start or date_end are None
                      or set to datetime delta between date_start and date_end
    :param period_type: one of: 'year', 'quarter', 'month', 'week', 'day', 'hour', 'minute', 'second'.
                        If None, date_start and date_end must be different from None (otherwise, an error is raised),
                        nb_period and full_periods arguments are ignored and then [(date_start, date_end)] is returned.
    :param reset_periods: if True, get first date of periods
    :return: list of tuples of date_start (to include), date_end (to exclude)
    """
    if date_start and date_end:  # use the min of nb_month and date_end - date_start
        if date_end < date_start:
            date_start, date_end = date_end, date_start
        if period_type is None:  # particular case
            return [(pd.to_datetime(date_start), pd.to_datetime(date_end))]
        nb_period = np.inf if nb_period is None else nb_period
        nb_period = min(nb_period, datetime_delta(date_start, date_end, period_type=period_type))
        date_end = None
    if nb_period is None:
        nb_period = 1
    if nb_period < 1:
        return []
    if not date_start and not date_end:
        date_end = datetime.datetime.now()
    if date_start:
        date_start = reset_period(date_start, period_type=period_type) if reset_periods else date_start
        dates = [add_period(date_start, i, period_type=period_type) for i in range(nb_period)]
    elif date_end:
        date_end = reset_period(date_end, period_type=period_type) if reset_periods else date_end
        dates = [add_period(date_end, -i - 1, period_type=period_type) for i in range(nb_period)]
        dates.reverse()
    periods = [(date, add_period(date, 1, period_type=period_type)) for date in dates]
    return periods


def get_month_periods(date_start=None, date_end=None, nb_period=1):
    """Returns nb_period month periods between date_start and date_end. See get_periods."""
    return get_periods(date_start=date_start, date_end=date_end, nb_period=nb_period, period_type='month')
