"""
Parser for the _rpc.txt file format.
"""
from __future__ import annotations  # noqa

import maxar_tiny_rpc.reader.common as c

from parsy import Parser, seq
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
    return seq(c.key() << c.colon(), c.number())
