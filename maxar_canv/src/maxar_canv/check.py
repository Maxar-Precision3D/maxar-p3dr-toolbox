from __future__ import annotations  # noqa

import pathlib
from typing import Any, Callable, Dict


def is_positive_int(x: Any) -> bool:
    """
    Check that an argument is an integer, and greater than zero.

    Parameters:
        x: The argument to check.

    Returns:
        True or False.
    """
    return isinstance(x, int) and x > 0


def is_float(x: Any) -> bool:
    """
    Check that an argument is a floating point number.

    Parameters:
        x: The argument to check.

    Returns:
        True or False.
    """
    return isinstance(x, float)


def is_list_of(xs: list[Any], exp_len: int, pred: Callable[[Any], bool]) -> bool:
    """
    Check that a list is composed of the expected parts.

    Parameters:
        xs: The list.
        exp_len: The expected length.
        pred: The predicate function to determine list content.

    Returns:
        True or False.
    """
    is_ok = isinstance(xs, list) and len(xs) == exp_len

    if is_ok:
        for x in xs:
            is_ok &= pred(x)

    return is_ok


def is_canv_index(obj: Dict[str, Any]) -> bool:
    """
    Check that an arguments is an object matching the Canv index file.

    Parameters:
        obj: The object.

    Returns:
        True or False.
    """
    try:
        is_ok = isinstance(obj['version'], int) and obj['version'] >= 4
        is_ok &= is_positive_int(obj['frame-count'])
        is_ok &= is_list_of(obj['image-size'], 2, is_positive_int)

        path = pathlib.Path(obj['canonic-video-path'])
        is_ok &= not path.is_absolute() and path.suffix == '.ims'

        return is_ok
    except KeyError:
        return False
    except TypeError:
        return False


def is_ims_index(obj: Dict[str, Any]) -> bool:
    """
    Check that an arguments is an object matching the Ims index file.

    Parameters:
        obj: The object.

    Returns:
        True or False.
    """
    try:
        is_ok = isinstance(obj['version'], int) and obj['version'] >= 4
        is_ok &= is_positive_int(obj['frame-count'])

        return is_ok
    except KeyError:
        return False
    except TypeError:
        return False


def is_proc(objs: list[Dict[str, Any]]) -> bool:
    """
    Check that an argument is a list of objects with expected content.

    Parameters:
        objs: The list.

    Returns:
        True or False.
    """
    try:
        is_ok = isinstance(objs, list)

        if is_ok and len(objs) > 0:
            for obj in objs:
                is_ok &= isinstance(obj['cmds'], list)
                is_ok &= isinstance(obj['pwin'], str)

        return is_ok
    except KeyError:
        return False
    except TypeError:
        return False


def is_metadata(obj: Dict[str, Any]) -> bool:
    """
    Check that an argument is an object matching metadata.

    Parameters:
        obj: The object.

    Returns:
        True or False.
    """
    try:
        cam = obj['cam']

        is_ok = is_list_of(cam['pos'], 3, is_float)
        is_ok &= is_list_of(cam['att'], 3, is_float)

        lens = cam['lens']
        is_ok &= is_float(lens['vfov'])
        is_ok &= is_float(lens['hfov'])

        if 'k2' in lens:
            is_ok &= is_float(lens['k2'])
        if 'k3' in lens:
            is_ok &= is_float(lens['k3'])
        if 'k4' in lens:
            is_ok &= is_float(lens['k4'])

        return is_ok
    except KeyError:
        return False
    except TypeError:
        return False
