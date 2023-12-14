from .rpc import Rpc

import argparse
import pathlib
import sys

def main() -> bool:
    parser = argparse.ArgumentParser('python -m maxar_tiny_rpc')
    parser.add_argument('rpcfile', metavar='RPC-file', type=pathlib.Path,
                        help='RPC-file (.RPB, .rpc or _rpc.txt)')
    args = parser.parse_args()

    rpc = Rpc.from_file(args.rpcfile)
    if rpc is not None:
        print('ok')
        return True
    else:
        print('not ok')
        return False

    return True


if __name__ == '__main__':
    try:
        sys.exit(0 if main() else 1)
    except Exception as e:
        print(f"Caught: '{e}")
        sys.exit(1)
