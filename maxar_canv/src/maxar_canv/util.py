from __future__ import annotations  # noqa

import math
import pathlib
from typing import Any, Callable
import zipfile


def nth_file(num: int, count: int, suffix: str) -> str:
    """
    Utility to generate a numeric filename.

    Parameters:
        num: The number of the file (must be less or equal to the count).
        count: The total number of items in the set.
        suffix: The file suffix.

    Returns:
        The filename, with leading zeros if necessary.
    """
    assert num <= count

    digits = math.floor(math.log10(count)) + 1
    return str(num).zfill(digits) + suffix


def nth_meta(num: int, count: int) -> str:
    """
    Utility to generate a numeric filename.

    Parameters:
        num: The number of the file (must be less or equal to the count).
        count: The total number of items in the set.        

    Returns:
        The filename, with leading zeros if necessary.
    """
    return nth_file(num, count, '.json')


def nth_image(num: int, count: int) -> str:
    """
    Utility to generate a numeric filename.

    Parameters:
        num: The number of the file (must be less or equal to the count).
        count: The total number of items in the set.        

    Returns:
        The filename, with leading zeros if necessary.
    """
    return nth_file(num, count, '.jpeg')


def with_exceptions(path: pathlib.Path, f: Callable[[pathlib.Path], Any]) -> Any:
    """
    Helper function to wrap exceptions while reading a zip archive.

    Parameters:
        path: The path to a zip-archive.
        f: A function to work on the zip-archive.

    Return:
        None if anything fails, otherwise the value from the function f.
    """
    try:
        if path.exists() and zipfile.is_zipfile(path):
            return f(path)
        else:
            print(f"'{path}' is not a valid or readable zip-file")
            return None
    except KeyError as e:
        print(f"Key Error: '{e}'")
        return None
    except zipfile.BadZipFile as e:
        print(f'{e}')
        return None
