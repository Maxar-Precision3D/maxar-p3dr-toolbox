from __future__ import annotations  # noqa

import argparse
from itertools import islice
import pathlib
import sys
from typing import Any, Dict

from maxar_canv import Canv, Ims, Playback, validate_canv, validate_ims


def command_line() -> str:
    """
    Utility to get the complete command line as a string.
    """
    cmd = 'python -m canv'

    for arg in sys.argv[1:]:
        cmd += ' ' + arg

    return cmd


def do_validate_ims(path: pathlib.Path) -> bool:
    """
    Validate a standalone Ims-file.
    """
    if validate_ims(path):
        print("Validation says 'ok'")
        return True
    else:
        print("Validation says 'nope'")
        return False


def do_validate_canv(path: pathlib.Path) -> bool:
    """
    Validate a Canv-file (and its linked Ims-file).
    """
    if validate_canv(path):
        print("Validation says 'ok'")
        return True
    else:
        print("Validation says 'nope'")
        return False


def do_probe_canv(path: pathlib.Path) -> bool:
    """
    Probe a Canv-file (and its linked Ims-file).
    """
    canv = Canv.from_file(path)
    if canv is None:
        return False

    ims = Ims.from_file(canv.ims_path())
    if ims is None:
        return False

    def probe_proc(proc: list[Dict[str, Any]]) -> None:
        for i, obj in enumerate(proc):
            print(f'  BeginProc(index={i})')
            if 'cmds' in obj:
                print('    BeginGenesis()')
                for cmd in obj['cmds']:
                    print(f'      Cmd({cmd})')
                print('    EndGenesis()')
            if 'pwin' in obj:
                print(f"    Pwin({obj['pwin']})")
            print('  EndProc()')

    print(f'BeginCanv({path})')
    print(f'  Version({canv.version()})')
    print(f'  FrameCount({canv.frame_count()})')
    print('  BeginImageSize(nominal)')
    width, height = canv.image_size()
    print(f'    Width({width})')
    print(f'    Height({height})')
    print('  EndImageSize()')
    probe_proc(canv._proc)
    print('EndCanv()')

    print(f'BeginIms({canv.ims_path()})')
    print(f'  Version({ims.version()})')
    print(f'  FrameCount({ims.frame_count()})')
    print('  BeginImageSize(actual)')
    image = ims.read(0)
    if image is not None:
        print(f'    Width({image.width})')
        print(f'    Height({image.height})')
    print('  EndImageSize()')
    probe_proc(ims._proc)
    print('EndIms()')

    return True


def do_slice_canv(source_canv_path: pathlib.Path,
                  target_canv_path: pathlib.Path,
                  range: (tuple[int, int] | None),
                  image_size: (tuple[int, int] | None)) -> bool:
    """
    Slice a Canv-file (and its linked Ims-file).

    Parameters:
        source_canv_path: The source Canv-file path.
        target_canv_path: The target Canv-file path.
        range: The frame range for the slice (from, to). If None the
               complete range is used.
        image_size: The image size to convert to for the target
                    Canv-file (width, height). If None the
                    original image size is used.

    Returns:
        True if successful, otherwise False.
    """

    # Check and prepare source and target file paths.
    if target_canv_path.suffix != '.canv':
        print("The target Canv-file path must have the suffix '.canv'")
        return False

    if target_canv_path.is_file():
        print('The target Canv-file already exist')
        return False

    target_ims_path = target_canv_path.with_suffix('.ims')
    if target_ims_path.is_file():
        print(f"The target Ims-file '{target_ims_path}' already exist")
        return False

    source_canv = Canv.from_file(source_canv_path)
    if source_canv is None:
        return False

    source_ims = Ims.from_file(source_canv.ims_path())
    if source_ims is None:
        return False

    if source_canv.frame_count() != source_ims.frame_count():
        print('Number of frames differ between Canv and Ims')
        return False

    # Check range and image_size.
    if range is None:
        range = (0, source_canv.frame_count())
    else:
        start, end = range
        if start > end or start < 0 or end < 0:
            print('Range start must be <= range end and range cannot be negative')
            return False
        elif end > source_canv.frame_count():
            print('Range cannot be beyond the range of the source')
            return False

    frame_count = range[1] - range[0]
    if frame_count == 0:
        print('The number of frames must be at least one')
        return False

    resize = False
    if image_size is not None:
        target_width, target_height = image_size
        source_width, source_height = source_canv._index['image-size']
        resize = True
        if target_width < 1 or target_width > source_width or \
                target_height < 1 or target_height > source_height:
            print(
                'Image size must be greater than one, and not greater than source image')
            return False
    else:
        image_size = tuple(source_canv._index['image-size'])

    # Create new Canv and Ims. Inherit proc from source files.
    target_canv = Canv.new(path=target_canv_path,
                           frame_count=frame_count,
                           image_size=image_size,
                           ims_path=target_ims_path,
                           proc=source_canv._proc
                           )
    target_ims = Ims.new(path=target_ims_path,
                         frame_count=frame_count,
                         proc=source_ims._proc)

    # Append the current command to the proc history.
    cmd = command_line()
    target_canv.append_command(cmd, tag='0.0.1')
    target_ims.append_command(cmd, tag='0.0.1')

    # Iterate over the selected slice and write the new Canv and Ims.
    for data in islice(Playback(source_canv, source_ims), range[0], range[1]):
        if data is not None:
            metadata, image = data

            image = image.resize(image_size) if resize else image
            target_canv.append(metadata)
            target_ims.append(image)
        else:
            print('Playback of source failed')
            return False

    # Done!
    return True


def main() -> bool:
    parser = argparse.ArgumentParser('python -m canv')
    parser.add_argument('--validate-ims', type=pathlib.Path,
                        metavar='SOURCE_PATH', help='Validate a standalone Ims-file')
    parser.add_argument('--validate-canv', type=pathlib.Path,
                        metavar='SOURCE_PATH', help='Validate a Canv-file (and its linked Ims-file)')
    parser.add_argument('--probe-canv', type=pathlib.Path,
                        metavar='SOURCE_PATH', help='Probe a Canv-file (and its linked Ims-file)')
    parser.add_argument('--slice-canv', type=pathlib.Path, nargs=2,
                        metavar=('SOURCE_PATH', 'TARGET_PATH'),
                        help='Slice a Canv-file (and its linked Ims-file)')
    parser.add_argument('--range', type=int, nargs=2,
                        metavar=('FROM_FRAME', 'TO_FRAME'),
                        help='The range of frames for slicing (optional)')
    parser.add_argument('--image-size', type=int, nargs=2,
                        metavar=('WIDTH', 'HEIGHT'),
                        help='New image size for slicing (optional)')
    options = parser.parse_args()

    if options.validate_ims is not None:
        return do_validate_ims(options.validate_ims)
    elif options.validate_canv is not None:
        return do_validate_canv(options.validate_canv)
    elif options.probe_canv is not None:
        return do_probe_canv(options.probe_canv)
    elif options.slice_canv is not None:
        range = tuple(options.range) if options.range is not None else None
        image_size = tuple(
            options.image_size) if options.image_size is not None else None
        return do_slice_canv(options.slice_canv[0], options.slice_canv[1],
                             range, image_size)
    else:
        parser.print_usage()

    return False


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
