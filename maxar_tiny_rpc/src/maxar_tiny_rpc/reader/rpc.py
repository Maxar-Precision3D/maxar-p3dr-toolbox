"""
Parser for the .rpc file format.
"""
from __future__ import annotations  # noqa

import maxar_tiny_rpc.reader.common as c

from parsy import Parser, regex, seq, string
from typing import Any, Dict


def parse(content: str) -> Dict[str, Any]:
    """
    Parse _rpc.txt from the string and produce a normalized dictionary
    with the parsed data.
    """
    return c.remap(file().parse(content))


def file() -> Parser:
    return assignment().many()


def assignment() -> Parser:
    return seq(c.key() << c.colon(), degenerate_number() << unit().optional())


def degenerate_number() -> Parser:
    return c.lexeme(regex(r'[-\+]?([0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')).map(float)


def unit() -> Parser:
    return c.lexeme(string('pixels') | string('meters') | string('degrees'))
