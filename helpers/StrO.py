"""String Operations Module.

This module provides utility functions for common string operations
including case conversions, cleaning, and formatting.

Typical usage example:
    >>> from helpers.StrO import to_snake_case, to_camel_case, clean_string
    >>> to_snake_case("MyVariableName")
    'my_variable_name'
    >>> to_camel_case("my_variable_name")
    'myVariableName'

Attributes:
    to_snake_case: Convert a string to snake_case.
    to_camel_case: Convert a string to camelCase.
    clean_string: Remove non-alphanumeric characters from a string.

TODO(enhancement): Add to_pascal_case function.
TODO(enhancement): Add to_kebab_case function.
TODO(feature): Add string truncation with ellipsis.
"""

import re
from typing import Optional


def to_snake_case(s: str) -> str:
    """Convert a string to snake_case.

    This function converts various string formats (camelCase, PascalCase,
    kebab-case, space-separated, etc.) to snake_case format.

    Args:
        s: The input string to convert.

    Returns:
        The snake_case representation of the input string.

    Example:
        >>> to_snake_case("MyVariableName")
        'my_variable_name'
        >>> to_snake_case("my-variable-name")
        'my_variable_name'
        >>> to_snake_case("MY_VARIABLE")
        'my_variable'
        >>> to_snake_case("simpleTest")
        'simple_test'

    Note:
        Consecutive uppercase letters are treated as acronyms and kept
        together (e.g., "XMLParser" becomes "xml_parser").
    """
    # Replace spaces, hyphens, and existing underscores with single underscore
    s = re.sub(r"(\s|_|-)+", "_", s)
    # Handle acronyms followed by capitalized word
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    # Handle lowercase/digit followed by uppercase
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase.

    This function converts various string formats (snake_case, kebab-case,
    space-separated, etc.) to camelCase format.

    Args:
        s: The input string to convert.

    Returns:
        The camelCase representation of the input string.

    Example:
        >>> to_camel_case("my_variable_name")
        'myVariableName'
        >>> to_camel_case("my-variable-name")
        'myVariableName'
        >>> to_camel_case("My Variable Name")
        'myVariableName'

    Note:
        The first character is always lowercase in camelCase.
    """
    # Replace separators with spaces
    s = re.sub(r"(\s|_|-)+", " ", s)
    # Handle acronyms and case transitions
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", s)
    words = s.split()
    # First word lowercase, rest title case
    return words[0].lower() + "".join(w.title() for w in words[1:])


def clean_string(s: str, replace_with: str = " ") -> str:
    """Clean a string by removing non-alphanumeric characters.

    This function removes any characters that are not alphanumeric or
    whitespace, replacing them with the specified replacement character.

    Args:
        s: The input string to clean.
        replace_with: The character to replace non-alphanumeric characters
            with. Defaults to a space character.

    Returns:
        The cleaned string with non-alphanumeric characters replaced.

    Example:
        >>> clean_string("Hello, World!")
        'Hello  World '
        >>> clean_string("user@example.com", replace_with="")
        'userexamplecom'
        >>> clean_string("file-name.txt", replace_with="_")
        'file_name_txt'

    Note:
        Whitespace characters in the original string are preserved.
        Only special characters (punctuation, symbols) are replaced.
    """
    return re.sub(r"[^\w\s]", replace_with, s)