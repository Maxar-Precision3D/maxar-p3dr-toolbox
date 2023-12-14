from __future__ import annotations  # noqa

import maxar_tiny_rpc.reader.rpb as rpb
import maxar_tiny_rpc.reader.rpc as rpc
import maxar_tiny_rpc.reader.rpc_txt as rpc_txt

import numpy as np
from numpy.typing import NDArray
from parsy import ParseError
import pathlib
from typing import Any, Dict


def read_file(path: pathlib.Path) -> Dict[str, NDArray] | None:
    """
    Read a RPC file (.rpc, .RPB or _rpc.txt) from the given path.

    Parameters:
        path: Path to RPC file.

    Returns:
        A valid and normalized dictionary, or None if something fails. In case of fail
        a message is written to stdout.
    """
    if not path.is_file():
        print(f"Error: '{path}' is not a valid RPC file")
        return None

    try:
        with open(path, 'r') as f:
            content = f.read()

            if path.suffix == '.RPB':
                return normalize(rpb.parse(content))
            elif path.suffix == '.rpc':
                return normalize(rpc.parse(content))
            elif path.name.endswith('_rpc.txt'):
                return normalize(rpc_txt.parse(content))
            else:
                print(f"Error: '{path}' does not have a valid RPC file suffix")
                return None
    except KeyError as e:
        print(f"Error: '{path} missing key {e}")
        return None
    except ParseError as e:
        print(f"Error: '{path} {e}")
        return None


def normalize(data: Dict[str, Any]) -> Dict[str, NDArray]:
    image_off = np.empty(2, dtype=np.float64)
    image_off[0] = data['SAMP_OFF']
    image_off[1] = data['LINE_OFF']

    image_scale = np.empty(2, dtype=np.float64)
    image_scale[0] = data['SAMP_SCALE']
    image_scale[1] = data['LINE_SCALE']

    geo_off = np.empty(3, dtype=np.float64)
    geo_off[0] = data['LAT_OFF']
    geo_off[1] = data['LONG_OFF']
    geo_off[2] = data['HEIGHT_OFF']

    geo_scale = np.empty(3, dtype=np.float64)
    geo_scale[0] = data['LAT_SCALE']
    geo_scale[1] = data['LONG_SCALE']
    geo_scale[2] = data['HEIGHT_SCALE']

    samp_num_coeff = np.array(data['SAMP_NUM_COEFF'], dtype=np.float64)
    samp_den_coeff = np.array(data['SAMP_DEN_COEFF'], dtype=np.float64)
    line_num_coeff = np.array(data['LINE_NUM_COEFF'], dtype=np.float64)
    line_den_coeff = np.array(data['LINE_DEN_COEFF'], dtype=np.float64)

    return {
        'IMAGE_OFF': image_off,
        'IMAGE_SCALE': image_scale,
        'GEO_OFF': geo_off,
        'GEO_SCALE': geo_scale,
        'SAMP_NUM_COEFF': samp_num_coeff,
        'SAMP_DEN_COEFF': samp_den_coeff,
        'LINE_NUM_COEFF': line_num_coeff,
        'LINE_DEN_COEFF': line_den_coeff
    }
