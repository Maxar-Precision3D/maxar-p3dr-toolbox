from __future__ import annotations  # noqa

import json
from typing import Any, Dict
import zipfile

from .check import is_canv_index, is_ims_index, is_proc


class Base:
    """
    Base class for the canonical video format, i.e. both the Canv and Ims files.
    Shall not be used directory, instead use Canv or Ims.
    """

    VERSION = 4
    """
    The current version of the file format. Will be inserted into the index
    file when creating new files.
    """

    def __init__(self: Base,
                 archive: zipfile.ZipFile,
                 index: Dict[str, Any],
                 proc: list[Dict[str, Any]],
                 writable: bool) -> None:
        """
        Construct a new base object.

        Parameters:
            archive: The open zip-archive (open for reading or writing, 
            depending on how derived Canv or Ims was created.).
            index: Unpacked index structure (exact content depends
            on if Canv or Ims).
            proc: Proc structure.
            writable: Flag to tell whether the file is writable.
        """
        assert is_canv_index(index) or is_ims_index(index)
        assert is_proc(proc)

        self._archive = archive
        self._index = index
        self._proc = proc
        self._writable = writable

    def __del__(self: Base) -> None:
        """
        Deletion method, to make sure the archive is closed. And that
        metadata is written to archive if the file is writable.
        """
        if self._archive is not None:
            if self._writable:
                self._archive.writestr(
                    'index.json', json.dumps(self._index, indent=2))
                self._archive.writestr(
                    'proc.json', json.dumps(self._proc, indent=2))

            self._archive.close()

    def version(self: Base) -> int:
        """
        Get the file format version.

        Returns:
            The format version.
        """
        return self._index['version']

    def frame_count(self: Base) -> int:
        """
        Get the frame count.

        Returns:
            The frame count.
        """
        return self._index['frame-count']

    def proc(self: Base) -> list[Dict[str, Any]]:
        """
        Get the proc structure.

        Returns:
            The proc structure.
        """
        return self._proc

    def append_command(self: Base, cmd: str, tag: str) -> None:
        """
        Append a new command to the proc's command history.

        Parameters:
            cmd: The command string.
            tag: Version identification tag string.
        """
        for obj in self._proc:
            if obj['pwin'] == tag:
                # A matching proc object is found - append and return.
                obj['cmds'].append(cmd)
                return

        record = {
            'cmds': [
                cmd
            ],
            'pwin': tag
        }
        self._proc.append(record)
