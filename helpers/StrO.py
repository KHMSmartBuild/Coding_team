"""String Operations Module.

A utility module to handle common string operations including
case conversions, cleaning, and formatting.

Example:
    >>> from helpers.StrO import to_snake_case, to_camel_case
    >>> to_snake_case("HelloWorld")
    'hello_world'
    >>> to_camel_case("hello_world")
    'helloWorld'
"""

import re
from typing import Optional


def to_snake_case(s: str) -> str:
    """Convert a string to snake_case.

    Takes a string in various formats (camelCase, PascalCase, kebab-case,
    or with spaces) and converts it to snake_case.

    Args:
        s: The input string to convert.

    Returns:
        The snake_case representation of the input string.

    Example:
        >>> to_snake_case("HelloWorld")
        'hello_world'
        >>> to_snake_case("hello-world")
        'hello_world'
        >>> to_snake_case("Hello World")
        'hello_world'
    """
    s = re.sub(r"(\s|_|-)+", "_", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1_\2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1_\2", s)
    return s.lower()


def to_camel_case(s: str) -> str:
    """Convert a string to camelCase.

    Takes a string in various formats (snake_case, kebab-case,
    or with spaces) and converts it to camelCase.

    Args:
        s: The input string to convert.

    Returns:
        The camelCase representation of the input string.
        Returns an empty string if the input is empty or whitespace only.

    Example:
        >>> to_camel_case("hello_world")
        'helloWorld'
        >>> to_camel_case("hello-world")
        'helloWorld'
        >>> to_camel_case("Hello World")
        'helloWorld'
        >>> to_camel_case("")
        ''
    """
    s = re.sub(r"(\s|_|-)+", " ", s)
    s = re.sub(r"([A-Z]+)([A-Z][a-z])", r"\1 \2", s)
    s = re.sub(r"([a-z\d])([A-Z])", r"\1 \2", s)
    words = s.split()
    if not words:
        return ""
    return words[0].lower() + "".join(w.title() for w in words[1:])


def to_pascal_case(s: str) -> str:
    """Convert a string to PascalCase.

    Takes a string in various formats and converts it to PascalCase
    (also known as UpperCamelCase).

    Args:
        s: The input string to convert.

    Returns:
        The PascalCase representation of the input string.
        Returns an empty string if the input is empty.

    Example:
        >>> to_pascal_case("hello_world")
        'HelloWorld'
        >>> to_pascal_case("hello-world")
        'HelloWorld'
        >>> to_pascal_case("")
        ''
    """
    camel = to_camel_case(s)
    if not camel:
        return ""
    return camel[0].upper() + camel[1:]


def to_kebab_case(s: str) -> str:
    """Convert a string to kebab-case.

    Takes a string in various formats and converts it to kebab-case
    (lowercase words separated by hyphens).

    Args:
        s: The input string to convert.

    Returns:
        The kebab-case representation of the input string.

    Example:
        >>> to_kebab_case("HelloWorld")
        'hello-world'
        >>> to_kebab_case("hello_world")
        'hello-world'
    """
    return to_snake_case(s).replace("_", "-")


def clean_string(s: str, replace_with: str = " ") -> str:
    """Clean a string by removing non-alphanumeric characters.

    Removes any characters that are not alphanumeric or whitespace,
    replacing them with the specified character.

    Args:
        s: The input string to clean.
        replace_with: The character to replace non-alphanumeric
            characters with. Defaults to a space.

    Returns:
        The cleaned string with non-alphanumeric characters replaced.

    Example:
        >>> clean_string("Hello, World!")
        'Hello  World '
        >>> clean_string("test@email.com", "_")
        'test_email_com'
    """
    return re.sub(r"[^\w\s]", replace_with, s)


def truncate(s: str, max_length: int, suffix: str = "...") -> str:
    """Truncate a string to a maximum length.

    If the string exceeds the maximum length, it is truncated and
    the suffix is appended.

    Args:
        s: The input string to truncate.
        max_length: The maximum length of the output string
            (including suffix).
        suffix: The suffix to append if truncated. Defaults to "...".

    Returns:
        The truncated string with suffix if needed.

    Raises:
        ValueError: If max_length is less than the length of suffix.

    Example:
        >>> truncate("Hello, World!", 10)
        'Hello, ...'
        >>> truncate("Hi", 10)
        'Hi'
    """
    if max_length < len(suffix):
        raise ValueError("max_length must be at least the length of suffix")
    if len(s) <= max_length:
        return s
    return s[: max_length - len(suffix)] + suffix


def slugify(s: str) -> str:
    """Convert a string to a URL-friendly slug.

    Converts the string to lowercase, removes special characters,
    and replaces spaces with hyphens.

    Args:
        s: The input string to slugify.

    Returns:
        A URL-friendly slug version of the string.

    Example:
        >>> slugify("Hello World!")
        'hello-world'
        >>> slugify("Python is great")
        'python-is-great'
    """
    s = s.lower()
    s = re.sub(r"[^\w\s-]", "", s)
    s = re.sub(r"[-\s]+", "-", s).strip("-")
    return s


def is_empty_or_whitespace(s: Optional[str]) -> bool:
    """Check if a string is empty or contains only whitespace.

    Args:
        s: The input string to check. Can be None.

    Returns:
        True if the string is None, empty, or contains only whitespace.

    Example:
        >>> is_empty_or_whitespace("")
        True
        >>> is_empty_or_whitespace("   ")
        True
        >>> is_empty_or_whitespace("hello")
        False
    """
    return s is None or s.strip() == ""