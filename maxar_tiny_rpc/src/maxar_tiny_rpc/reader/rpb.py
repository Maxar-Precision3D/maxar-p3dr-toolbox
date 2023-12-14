"""
Parser for the RPB file format.
"""
from __future__ import annotations  # noqa

import maxar_tiny_rpc.reader.common as c

from parsy import Parser, seq, string
from typing import Any, Dict


def parse(content: str) -> Dict[str, Any]:
    """
    Parse RPB from the string and produce a normalized dictionary with
    the parsed data.

    Parameters:
        content: RPB file data as a string.

    Returns:
        Dictionary with parsed values.
    """
    _, data, _, _ = file().parse(content)

    return remap(data)


def remap(data: list) -> Dict[str, Any]:
    map = {
        'errBias': 'ERR_BIAS',
        'errRand': 'ERR_RAND',
        'lineOffset': 'LINE_OFF',
        'sampOffset': 'SAMP_OFF',
        'latOffset': 'LAT_OFF',
        'longOffset': 'LONG_OFF',
        'heightOffset': 'HEIGHT_OFF',
        'lineScale': 'LINE_SCALE',
        'sampScale': 'SAMP_SCALE',
        'latScale': 'LAT_SCALE',
        'longScale': 'LONG_SCALE',
        'heightScale': 'HEIGHT_SCALE',
        'lineNumCoef': 'LINE_NUM_COEFF',
        'lineDenCoef': 'LINE_DEN_COEFF',
        'sampNumCoef': 'SAMP_NUM_COEFF',
        'sampDenCoef': 'SAMP_DEN_COEFF'
    }

    # Rename keys to upper case style.
    rpc = dict()
    for key, value in data:
        rpc[map[key]] = value

    return rpc


def file() -> Parser:
    return seq(assignment().many(),
               group_begin() >> assignment().many() << group_end(),
               end_file(), c.semicolon())


def string_literal() -> Parser:
    return c.quote() >> c.key() << c.quote()


def array() -> Parser:
    return c.lparen() >> (c.number() << c.comma().optional()).many() << c.rparen()


def assignment() -> Parser:
    return seq(c.key() << c.equals(), (c.number() | string_literal() | array()) << c.semicolon())


def group_begin() -> Parser:
    return c.lexeme(string('BEGIN_GROUP = IMAGE'))


def group_end() -> Parser:
    return c.lexeme(string('END_GROUP = IMAGE'))


def end_file() -> Parser:
    return c.lexeme(string('END'))
