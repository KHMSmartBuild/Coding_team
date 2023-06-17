# StrO.py - String Operations
# A utility script to handle common string operations.
# Typical uses include case conversions, cleaning, and formatting.
# Save this script in the project's "utilities" or "helpers" folder.

import re

def to_snake_case(s: str) -> str:
    """
    Convert a string to snake_case.

    :param s: The input string.
    :return: The snake_case representation of the input string.
    """
    s = re.sub(r"(\s|_|-)+", "_", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()

def to_camel_case(s: str) -> str:
    """
    Convert a string to camelCase.

    :param s: The input string.
    :return: The camelCase representation of the input string.
    """
    s = re.sub(r"(\s|_|-)+", " ", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", s)
    words = s.split()
    return words[0].lower() + "".join(w.title() for w in words[1:])

def clean_string(s: str, replace_with: str = " ") -> str:
    """
    Clean a string by removing any non-alphanumeric characters.

    :param s: The input string.
    :param replace_with: The character to replace non-alphanumeric characters with.
    :return: The cleaned string.
    """
    return re.sub(r"[^\w\s]", replace_with, s)

# TODO: Add more string operations as needed.

"""

Script name: String Operations
Filename: StrO.py
Description: A utility script to handle common string operations.
Typical uses: This script can be used for string manipulation tasks
 such as case conversions, cleaning, and formatting.
Typical locations: This script can be saved in the 
project's "utilities" or "helpers" folder.
Purpose and functions: The purpose of this script is to simplify 
and streamline string operations within the project. 
Functions include case conversions, cleaning, and formatting.

"""