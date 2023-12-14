import pathlib

from .canv import Canv
from .ims import Ims
from .playback import Playback  # noqa


def validate_canv(path: pathlib.Path) -> bool:
    """
    Helper function to validate a Canv-file and its linked Ims-file.

    Parameters:
        path: Path to Canv-file.

    Returns:
        The validation result.
    """
    canv = Canv.from_file(path, deep_validate=True)
    if canv is None:
        return False

    return validate_ims(canv.ims_path())


def validate_ims(path: pathlib.Path) -> bool:
    """
    Helper function to validate a standalone Ims-file.

    Parameters:
        path: Path to Ims-file.

    Returns:
        The validation result.
    """
    return True if Ims.from_file(path, deep_validate=True) is not None else False
