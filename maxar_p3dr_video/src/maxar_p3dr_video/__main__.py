from __future__ import annotations  # noqa

import argparse
import os
import pathlib
import sys
from urllib.parse import urlparse

from maxar_canv import Canv, Playback
from maxar_p3dr_video import CanvRegistrator, Server


def tcp_server_as_network_url(url: str) -> tuple[str, int] | None:
    split = urlparse(url)
    if split.scheme == 'tcp' and split.netloc != '' and split.port is not None:
        return split.netloc.split(':')[0], split.port
    else:
        return None


def check_references(references: list[pathlib.Path]) -> bool:
    for reference in references:
        if reference.suffix != '.r3db' or not reference.is_file():
            return False

    return True


def command_line() -> str:
    cmd = 'python -m maxar_p3dr_video'

    for arg in sys.argv[1:]:
        cmd += ' ' + arg

    return cmd


def main() -> bool:
    """
    Register a Canonic video using the Server. The source Ims-file is
    preserved while a new Canv-file is produced.
    """
    parser = argparse.ArgumentParser('python -m maxar_p3dr_video')
    parser.add_argument('canv', type=pathlib.Path,
                        metavar='Canv-File',
                        help='Maxar Canv-file for georegistration')
    parser.add_argument('-s', '--server', type=str,
                        required=True,
                        help='TCP url or file path to video server')
    parser.add_argument('-r', '--in-references', nargs='+',
                        metavar='REFERENCE',
                        type=pathlib.Path,
                        required=True,
                        help='Reference dataset(s) for the georegistration')
    parser.add_argument('-o', '--out-dir',
                        metavar='OUTPUT DIRECTORY',
                        type=pathlib.Path,
                        required=True,
                        help='Directory where to put the registered Canv-file')
    parser.add_argument('-n', '--out-name',
                        metavar='OUTPUT NAME',
                        type=pathlib.Path,
                        help='Name of registered Canv-file (if not set, it inherits input name)')
    parser.add_argument('-l', '--log', choices=['debug', 'info', 'warning', 'error'],
                        metavar='SEVERITY',
                        required=False,
                        default='warning',
                        help='Log severity for the video server {debug, info, warning, error}')
    parser.add_argument('-f', '--in-flight', choices=range(1, 15),
                        metavar='FRAMES IN FLIGHT',
                        type=int,
                        required=False,
                        default=10,
                        help="Threshold for the max number of simultaneous frames in flight")
    opts = parser.parse_args()

    # Check that the input file exists.
    input_file = opts.canv.absolute()
    if not input_file.is_file():
        print(f"'{input_file}' is a non-existing input file")
        return False

    # Check that the references are ok.
    if not check_references(opts.in_references):
        print('References does not exist or does not have expected suffix')
        return False
    references = [reference.resolve() for reference in opts.in_references]

    # Check that the output directory exist.
    output_dir = opts.out_dir
    if not output_dir.is_dir():
        print(f"'{output_dir}' is not a valid output directory")
        return False

    # Construct the name for the output file.
    output_file = output_dir / \
        (opts.out_name if opts.out_name is not None else input_file.name)

    # Output file must have .canv suffix.
    if output_file.suffix != '.canv':
        print(f"Output file '{output_file}' must have the suffix '.canv'")
        return False

    # Input and output file must not be the same.
    if input_file == output_file:
        print('Output file cannot be the same as the input file')
        return False

    # Open the input Canv video as a Playback.
    input_video = Playback.from_file(input_file)
    if input_video is None:
        return False

    # Get the relative path for the Ims file.
    abs_ims_path = input_video._canv.ims_path()
    rel_ims_path = pathlib.Path(os.path.relpath(abs_ims_path, output_file.parent))

    # Create playback object for the input video.
    playback = Playback.from_file(input_file)
    if playback is None:
        return False

    # Create the new registered Canv-file.
    reg_canv = Canv.new(path=output_file,
                        frame_count=playback._canv.frame_count(),
                        image_size=playback._canv.image_size(),
                        ims_path=rel_ims_path,
                        proc=playback._canv.proc())

    # Add the current command to the new canv.
    reg_canv.append_command(cmd=command_line(), tag='0.0.1')

    # Check what type of server that is requested, and run the
    # registration with that server.
    network_url = tcp_server_as_network_url(opts.server)
    if network_url is not None:
        host, port = network_url
        with Server.public_server(host=host, port=port) as server:
            registrator = CanvRegistrator(server=server,
                                          max_in_flight=opts.in_flight)
            registrator.run(playback=playback,
                            canv=reg_canv,
                            references=references)
    else:
        with Server.private_server(server_path=pathlib.Path(opts.server),
                                   severity=opts.log) as server:
            registrator = CanvRegistrator(server=server,
                                          max_in_flight=opts.in_flight)
            registrator.run(playback=playback,
                            canv=reg_canv,
                            references=references)

    return True


if __name__ == '__main__':
    sys.exit(0 if main() else 1)
