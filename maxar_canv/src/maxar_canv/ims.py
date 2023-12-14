from __future__ import annotations  # noqa

import json
import pathlib
from PIL import Image
from typing import Any, Dict
import zipfile

from .base import Base
from .check import is_ims_index, is_proc
from .util import nth_image, with_exceptions


class Ims(Base):
    """
    Class for the Ims flavour of the canonical video format.
    """

    @staticmethod
    def from_file(path: pathlib.Path, deep_validate: bool = False) -> (Ims | None):
        """
        Construct an Ims object from a file.

        Parameters:
            path: The path to the Ims-file.
            deep_validate: Flag to tell if deep validation shall be made.

        Returns:
            The Ims object, or None if validation fails.
        """

        def build_ims(path: pathlib.Path) -> (Ims | None):
            is_ok = True

            archive = zipfile.ZipFile(path, mode='r')
            index = json.loads(archive.read('index.json'))
            if not is_ims_index(index):
                print(
                    f"File 'index.json' in '{path}' does not fill requirements")
                is_ok = False

            proc = json.loads(archive.read('proc.json'))
            if not is_proc(proc):
                print(
                    f"File 'proc.json' in '{path}' does not fill requirements")
                is_ok = False

            if deep_validate:
                frame_count = index['frame-count']
                filelist = archive.namelist()
                for frame_nr in range(frame_count):
                    jpeg_name = nth_image(frame_nr, frame_count)
                    if not jpeg_name in filelist:
                        print(f"Image '{jpeg_name}' is missing in '{path}'")
                        is_ok = False

            if is_ok:
                return Ims(archive=archive, index=index, proc=proc, writable=False)
            else:
                return None

        return with_exceptions(path, build_ims)

    @staticmethod
    def new(path: pathlib.Path, frame_count: int, proc: list[Dict[str, Any]]) -> Ims:
        """
        Create a new Ims file.

        Parameters:
            path: Path to the new Ims-file.
            frame_count: The number of frames for the file.

        Returns:
            The Ims object.
        """
        archive = zipfile.ZipFile(path, mode='w')
        index = {
            'version': Base.VERSION,
            'frame-count': frame_count
        }
        return Ims(archive=archive, index=index, proc=proc, writable=True)

    def __init__(self: Ims,
                 archive: zipfile.ZipFile,
                 index: Dict[str, Any],
                 proc: list[Dict[str, Any]],
                 writable: bool) -> None:
        """
        Initialize a new Ims. Do not use Ims() directly, use from_file or new instead.
        """
        super().__init__(archive, index, proc, writable)
        self._frame_nr = 0

    def append(self: Ims, image: Image.Image) -> bool:
        """
        Append a new Image to the Ims-object. Is only valid for writable
        objects.

        Parameters:
            image: A PIL image.

        Returns:
            True if the append was successful (i.e. within the frame count range).
        """
        assert self._writable
        assert isinstance(image, Image.Image)

        if self._frame_nr < self.frame_count():
            jpeg_name = nth_image(self._frame_nr, self.frame_count())
            with self._archive.open(jpeg_name, 'w') as file:
                image.save(
                    file, 'jpeg', icc_profile=image.info.get('icc_profile'))
            self._frame_nr += 1

            return True
        else:
            return False

    def read(self: Ims, index: int) -> (Image.Image | None):
        """
        Read the indexed image from the Ims-object. Is only
        valid for non writable objects.

        Parameters:
            index: The requested index.

        Returns:
            The PIL Image if successful, else None.
        """
        assert not self._writable

        if index < self.frame_count():
            jpeg_name = nth_image(index, self.frame_count())
            return Image.open(self._archive.open(jpeg_name, 'r'), formats=['jpeg'])
        else:
            return None
