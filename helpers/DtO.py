"""Datetime Operations Module.

A utility module to handle common datetime operations including
parsing, formatting, and calculation of time intervals.

Example:
    >>> from helpers.DtO import parse_datetime, format_datetime
    >>> dt = parse_datetime("2024-01-15 10:30:00")
    >>> format_datetime(dt, "%B %d, %Y")
    'January 15, 2024'
"""

from datetime import datetime, timedelta, timezone
from typing import Optional, Union


def parse_datetime(
    s: str,
    fmt: str = "%Y-%m-%d %H:%M:%S",
) -> datetime:
    """Parse a datetime string and return a datetime object.

    Converts a string representation of a datetime to a datetime object
    using the specified format.

    Args:
        s: The input datetime string to parse.
        fmt: The format of the input datetime string.
            Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        A datetime object representing the input string.

    Raises:
        ValueError: If the string doesn't match the format.

    Example:
        >>> parse_datetime("2024-01-15 10:30:00")
        datetime.datetime(2024, 1, 15, 10, 30)
        >>> parse_datetime("15/01/2024", "%d/%m/%Y")
        datetime.datetime(2024, 1, 15, 0, 0)
    """
    return datetime.strptime(s, fmt)


def format_datetime(
    dt: datetime,
    fmt: str = "%Y-%m-%d %H:%M:%S",
) -> str:
    """Format a datetime object into a string.

    Converts a datetime object to a string representation using
    the specified format.

    Args:
        dt: The input datetime object to format.
        fmt: The desired format of the output datetime string.
            Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        A string representation of the datetime object.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 10, 30)
        >>> format_datetime(dt)
        '2024-01-15 10:30:00'
        >>> format_datetime(dt, "%B %d, %Y")
        'January 15, 2024'
    """
    return dt.strftime(fmt)


def time_since(
    dt: datetime,
    now: Optional[datetime] = None,
) -> str:
    """Calculate the time elapsed since a datetime.

    Returns a human-readable string describing the time interval
    between the given datetime and now.

    Args:
        dt: The input datetime object.
        now: An optional datetime object representing the current time.
            If not provided, uses the current time.

    Returns:
        A string representation of the time interval.

    Example:
        >>> from datetime import datetime, timedelta
        >>> past = datetime.now() - timedelta(hours=2)
        >>> time_since(past)
        '2:00:00'
    """
    if now is None:
        now = datetime.now()
    delta = now - dt
    return str(delta)


def time_until(
    dt: datetime,
    now: Optional[datetime] = None,
) -> str:
    """Calculate the time remaining until a datetime.

    Returns a human-readable string describing the time interval
    between now and the given datetime.

    Args:
        dt: The target datetime object.
        now: An optional datetime object representing the current time.
            If not provided, uses the current time.

    Returns:
        A string representation of the time interval.

    Example:
        >>> from datetime import datetime, timedelta
        >>> future = datetime.now() + timedelta(days=1)
        >>> time_until(future)
        '1 day, 0:00:00'
    """
    if now is None:
        now = datetime.now()
    delta = dt - now
    return str(delta)


def add_days(dt: datetime, days: int) -> datetime:
    """Add days to a datetime.

    Args:
        dt: The input datetime object.
        days: The number of days to add (can be negative).

    Returns:
        A new datetime object with the days added.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15)
        >>> add_days(dt, 10)
        datetime.datetime(2024, 1, 25, 0, 0)
    """
    return dt + timedelta(days=days)


def add_hours(dt: datetime, hours: int) -> datetime:
    """Add hours to a datetime.

    Args:
        dt: The input datetime object.
        hours: The number of hours to add (can be negative).

    Returns:
        A new datetime object with the hours added.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 10, 0)
        >>> add_hours(dt, 5)
        datetime.datetime(2024, 1, 15, 15, 0)
    """
    return dt + timedelta(hours=hours)


def days_between(start: datetime, end: datetime) -> int:
    """Calculate the number of days between two datetimes.

    Args:
        start: The start datetime.
        end: The end datetime.

    Returns:
        The number of days between the two datetimes.
        Returns a negative value if end is before start.

    Example:
        >>> from datetime import datetime
        >>> start = datetime(2024, 1, 1)
        >>> end = datetime(2024, 1, 15)
        >>> days_between(start, end)
        14
    """
    delta = end - start
    return delta.days


def is_past(dt: datetime, now: Optional[datetime] = None) -> bool:
    """Check if a datetime is in the past.

    Args:
        dt: The datetime to check.
        now: Optional reference datetime. Defaults to current time.

    Returns:
        True if the datetime is in the past, False otherwise.

    Example:
        >>> from datetime import datetime, timedelta
        >>> past = datetime.now() - timedelta(days=1)
        >>> is_past(past)
        True
    """
    if now is None:
        now = datetime.now()
    return dt < now


def is_future(dt: datetime, now: Optional[datetime] = None) -> bool:
    """Check if a datetime is in the future.

    Args:
        dt: The datetime to check.
        now: Optional reference datetime. Defaults to current time.

    Returns:
        True if the datetime is in the future, False otherwise.

    Example:
        >>> from datetime import datetime, timedelta
        >>> future = datetime.now() + timedelta(days=1)
        >>> is_future(future)
        True
    """
    if now is None:
        now = datetime.now()
    return dt > now


def get_current_timestamp() -> str:
    """Get the current UTC timestamp as an ISO 8601 string.

    Returns:
        The current timestamp in ISO 8601 format.

    Example:
        >>> get_current_timestamp()
        '2024-01-15T10:30:00+00:00'
    """
    return datetime.now(timezone.utc).isoformat()


def start_of_day(dt: datetime) -> datetime:
    """Get the start of the day for a datetime.

    Args:
        dt: The input datetime.

    Returns:
        A datetime representing midnight (00:00:00) of the same day.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 14, 30)
        >>> start_of_day(dt)
        datetime.datetime(2024, 1, 15, 0, 0)
    """
    return dt.replace(hour=0, minute=0, second=0, microsecond=0)


def end_of_day(dt: datetime) -> datetime:
    """Get the end of the day for a datetime.

    Args:
        dt: The input datetime.

    Returns:
        A datetime representing the last moment of the day (23:59:59.999999).
        The microsecond value ensures this is the absolute last instant before
        midnight of the next day.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 14, 30)
        >>> end_of_day(dt)
        datetime.datetime(2024, 1, 15, 23, 59, 59, 999999)
    """
    return dt.replace(hour=23, minute=59, second=59, microsecond=999999)