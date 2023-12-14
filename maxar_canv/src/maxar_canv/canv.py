from __future__ import annotations  # noqa

import json
import pathlib
from typing import Any, Dict
import zipfile

from .base import Base
from .check import is_canv_index, is_metadata, is_proc
from .util import nth_meta, with_exceptions


class Canv(Base):
    """
    Class for the Canv flavour of the canonical video format.
    """

    @staticmethod
    def from_file(path: pathlib.Path, deep_validate: bool = False) -> (Canv | None):
        """
        Construct a Canv object from a file.

        Parameters:
            path: The path to the Ims-file.
            deep_validate: Flag to tell if deep validation shall be made.

        Returns:
            The Canv object, or None if validation fails.
        """

        def build_canv(path: pathlib.Path) -> (Canv | None):
            is_ok = True

            archive = zipfile.ZipFile(path, mode='r')
            index = json.loads(archive.read('index.json'))
            if not is_canv_index(index):
                print(
                    f"File 'index.json' in '{path}' does not fill requirements")
                is_ok = False

            proc = json.loads(archive.read('proc.json'))
            if not is_proc(proc):
                print(
                    f"File 'proc.json' in '{path}' does not fill requirements")
                is_ok = False

            # is_canv_index has already checked that the canonic-video-path
            # is a relative path.
            ims_path = path.parent / index['canonic-video-path']
            if not ims_path.exists() or not ims_path.is_file():
                print(f"The Ims-path '{ims_path}' is invalid")
                is_ok = False

            if deep_validate:
                frame_count = index['frame-count']
                filelist = archive.namelist()
                for frame_nr in range(frame_count):
                    meta_name = nth_meta(frame_nr, frame_count)
                    if not meta_name in filelist:
                        print(f"Image '{meta_name}' is missing in '{path}'")
                        is_ok = False

            if is_ok:
                return Canv(archive=archive, index=index, proc=proc,
                            writable=False, ims_path=ims_path)
            else:
                return None

        return with_exceptions(path, build_canv)

    @staticmethod
    def new(path: pathlib.Path,
            frame_count: int,
            image_size: tuple[int, int],
            ims_path: pathlib.Path,
            proc: list[Dict[str, Any]]) -> Canv:
        """
        Create a new Canv file.

        Parameters:
            path: Path to the new Ims-file.
            frame_count: The number of frames for the file.

        Returns:
            The Ims object.
        """
        assert not ims_path.is_absolute()

        archive = zipfile.ZipFile(path, mode='w')
        index = {
            'version': Base.VERSION,
            'frame-count': frame_count,
            'image-size': list(image_size),
            'canonic-video-path': str(ims_path)
        }
        return Canv(archive=archive, index=index, proc=proc, writable=True, ims_path=ims_path)

    def __init__(self: Canv,
                 archive: zipfile.ZipFile,
                 index: Dict[str, Any],
                 proc: list[Dict[str, Any]],
                 writable: bool,
                 ims_path: pathlib.Path) -> None:
        """
        Initialize a new Canv. Do not use Canv() directly, use from_file or new instead.
        """
        super().__init__(archive, index, proc, writable)
        self._ims_path = ims_path
        self._frame_nr = 0

    def image_size(self: Canv) -> tuple[int, int]:
        """
        Get the image size for the Canv-file.

        Returns:
            The image size tuple (width, height).
        """
        return tuple(self._index['image-size'])

    def ims_path(self: Canv) -> pathlib.Path:
        """
        Get the linked Ims-file path.

        Returns:
            The filepath for the linked Ims-file.
        """
        return self._ims_path

    def append(self: Canv, obj: Dict[str, Any]) -> bool:
        """
        Append a new metadata to the Canv-object. Is only valid for writable
        objects.

        Parameters:
            obj: A JSON object rec

        Returns:
            True if the append was successful (i.e. within the frame count range).
        """
        assert self._writable
        assert is_metadata(obj)

        if self._frame_nr < self.frame_count():
            json_name = nth_meta(self._frame_nr, self.frame_count())
            self._archive.writestr(json_name, json.dumps(obj, indent=2))
            self._frame_nr += 1

            return True
        else:
            return False

    def read(self: Canv, index: int) -> (Dict[str, Any] | None):
        """
        Read the indexed metadata item from the Canv-object. Is only
        valid for non writable objects.

        Parameters:
            index: The requested index.

        Returns:
            The metadata object if successful, else None.
        """
        assert not self._writable

        if index < self.frame_count():
            json_name = nth_meta(index, self.frame_count())
            return json.loads(self._archive.read(json_name))
        else:
            return None
