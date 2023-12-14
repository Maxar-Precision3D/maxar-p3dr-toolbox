from __future__ import annotations # noqa

import pathlib
from PIL import Image
from typing import Any, Dict

from .canv import Canv
from .ims import Ims


class Playback:
    """
    Playback iterator for canonic video. Can be used together with
    itertools.islice to iterate a slice of the full sequence.
    """

    @staticmethod
    def from_file(path: pathlib.Path) -> (Playback | None):
        """ 
        Create a Playback iterator from a path to a Canv-file. The Ims-file
        will be discovered through the Canv-file.

        Parameters:
            path: Path to the Canv-file.

        Returns:
            A Playback object, or None if creation is failing.
        """
        canv = Canv.from_file(path)
        if canv is None:
            return None

        ims = Ims.from_file(canv.ims_path())
        if ims is None:
            return None

        if canv.frame_count() != ims.frame_count():
            print(
                f"Number of frames differ between '{path}' and '{canv.ims_path()}'")
            return None

        return Playback(canv, ims)

    def __init__(self: Playback, canv: Canv, ims: Ims) -> None:
        """
        Create a Playback iterator from a Canv object and an Ims object.

        Parameters:
            canv: The Canv object.
            ims: The Ims object.
        """
        assert canv.frame_count() == ims.frame_count()

        self._canv = canv
        self._ims = ims
        self._frame_nr = 0

    def __iter__(self: Playback) -> Playback:
        self._frame_nr = 0
        return self

    def __next__(self: Playback) -> (tuple[Dict[str, Any], Image.Image] | None):
        if self._frame_nr < self._canv.frame_count():
            meta = self._canv.read(self._frame_nr)
            image = self._ims.read(self._frame_nr)
            self._frame_nr += 1

            if not meta is None and not image is None:
                return meta, image
            else:
                return None
        else:
            raise StopIteration
