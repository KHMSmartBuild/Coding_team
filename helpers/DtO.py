"""Datetime Operations Module.

This module provides utility functions for common datetime operations
including parsing, formatting, and time interval calculations.

Typical usage example:
    >>> from helpers.DtO import parse_datetime, format_datetime, time_since, get_current_utc_timestamp
    >>> dt = parse_datetime("2024-01-15 14:30:00")
    >>> formatted = format_datetime(dt, "%Y-%m-%d")
    >>> elapsed = time_since(dt)
    >>> current_utc = get_current_utc_timestamp()

Attributes:
    parse_datetime: Parse a datetime string into a datetime object.
    format_datetime: Format a datetime object into a string.
    time_since: Calculate time elapsed since a datetime.
    get_current_utc_timestamp: Get the current UTC timestamp in ISO 8601 format.

TODO(enhancement): Add timezone support for parsing and formatting.
TODO(enhancement): Add function for calculating datetime differences in various units.
TODO(feature): Add support for relative time strings like "2 days ago".
"""

from datetime import datetime, timedelta, timezone
from typing import Optional


def parse_datetime(s: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """Parse a datetime string and return a datetime object.

    This function converts a string representation of a date/time into
    a Python datetime object using the specified format string.

    Args:
        s: The input datetime string to parse.
        fmt: The format string specifying the expected format of the input.
            Defaults to "%Y-%m-%d %H:%M:%S" (e.g., "2024-01-15 14:30:00").

    Returns:
        A datetime object representing the parsed date and time.

    Raises:
        ValueError: If the string cannot be parsed with the given format.

    Example:
        >>> dt = parse_datetime("2024-01-15 14:30:00")
        >>> print(dt.year)  # Output: 2024
        >>> dt = parse_datetime("15/01/2024", fmt="%d/%m/%Y")
        >>> print(dt.day)  # Output: 15
    """
    return datetime.strptime(s, fmt)


def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """Format a datetime object into a string.

    This function converts a datetime object into a string representation
    using the specified format string.

    Args:
        dt: The datetime object to format.
        fmt: The format string specifying the desired output format.
            Defaults to "%Y-%m-%d %H:%M:%S".

    Returns:
        A string representation of the datetime object.

    Example:
        >>> from datetime import datetime
        >>> dt = datetime(2024, 1, 15, 14, 30, 0)
        >>> format_datetime(dt)
        '2024-01-15 14:30:00'
        >>> format_datetime(dt, fmt="%B %d, %Y")
        'January 15, 2024'
    """
    return dt.strftime(fmt)


def time_since(dt: datetime, now: Optional[datetime] = None) -> str:
    """Calculate the time interval between a datetime and the current time.

    This function calculates and returns a human-readable string
    representing the time difference between the given datetime and now.

    Args:
        dt: The datetime object to calculate time since.
        now: Optional datetime object representing the current time.
            If not provided, uses the current system time.

    Returns:
        A string representation of the time interval (e.g., "1 day, 2:30:00").

    Example:
        >>> from datetime import datetime
        >>> past = datetime(2024, 1, 1, 0, 0, 0)
        >>> now = datetime(2024, 1, 2, 12, 0, 0)
        >>> time_since(past, now)
        '1 day, 12:00:00'
        >>> # Calculate from actual current time
        >>> time_since(datetime.now() - timedelta(hours=1))
        '1:00:00...'  # approximately

    Note:
        The returned string is the standard Python timedelta string
        representation, which may include days if applicable.
    """
    if now is None:
        now = datetime.now()
    delta = now - dt
    return str(delta)


def get_current_utc_timestamp() -> str:
    """Get the current UTC timestamp as an ISO 8601 string.

    This function returns the current time in UTC timezone formatted as
    an ISO 8601 string with timezone information (+00:00).

    Returns:
        The current UTC timestamp in ISO 8601 format (with timezone info).

    Example:
        >>> get_current_utc_timestamp()
        '2024-01-15T10:30:00+00:00'

    Note:
        The returned timestamp always includes UTC timezone information.
        Use this function when you need a standardized, timezone-aware
        timestamp for logging, API responses, or database records.
    """
    return datetime.now(timezone.utc).isoformat()