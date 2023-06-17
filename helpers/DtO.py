# DtO.py - Datetime Operations
# A utility script to handle common datetime operations.
# Typical uses include parsing, formatting, and calculation of time intervals.
# Save this script in the project's "utilities" or "helpers" folder.

from datetime import datetime, timedelta

def parse_datetime(s: str, fmt: str = "%Y-%m-%d %H:%M:%S") -> datetime:
    """
    Parse a datetime string and return a datetime object.

    :param s: The input datetime string.
    :param fmt: The format of the input datetime string.
    :return: A datetime object representing the input string.
    """
    return datetime.strptime(s, fmt)

def format_datetime(dt: datetime, fmt: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Format a datetime object into a string.

    :param dt: The input datetime object.
    :param fmt: The desired format of the output datetime string.
    :return: A string representation of the datetime object.
    """
    return dt.strftime(fmt)

def time_since(dt: datetime, now: datetime = None) -> str:
    """
    Calculate the time interval between a datetime object and the current time.

    :param dt: The input datetime object.
    :param now: An optional datetime object representing the current time.
    :return: A string representation of the time interval.
    """
    if now is None:
        now = datetime.now()
    delta = now - dt
    return str(delta)

# TODO: Add more datetime operations as needed.

"""
    Script name: Datetime Operations

Filename: DtO.py

Description: A utility script to handle common datetime operations.

Typical uses: This script can be used for datetime manipulation tasks
 such as parsing, formatting, and calculation of time intervals.

Typical locations: This script can be saved in the project's "utilities"
 or "helpers" folder.

Purpose and functions: The purpose of this script is to simplify and 
streamline datetime operations within the project. Functions include parsing, 
formatting, and time interval calculation.

Additional improvements or suggestions:

# Add functions for working with time zones and daylight saving time.
Implement more robust error handling for parsing and formatting operations.

# Add functions for calculating the difference between two datetime objects 
in various units (e.g., days, hours, minutes).


"""