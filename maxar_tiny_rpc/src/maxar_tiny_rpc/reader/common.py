"""
Common parser combinators etc.
"""
from __future__ import annotations  # noqa

from parsy import Parser, regex, string
from typing import Any, Dict


def lexeme(parser: Parser) -> Parser:
    """
    Combine the given parser with a postlude whitespace consumer.
    """
    return parser << whitespace()


def whitespace() -> Parser:
    """
    Parser that is consuming whitespace.
    """
    return regex(r'\s*')


def comma() -> Parser:
    """
    Parser that is accepting a comma.
    """
    return lexeme(string(','))


def colon() -> Parser:
    """
    Parser that is accepting a colon.
    """
    return lexeme(string(':'))


def lparen() -> Parser:
    """
    Parser that is accepting a left parenthesis.
    """
    return lexeme(string('('))


def rparen() -> Parser:
    """
    Parser that is accepting a right parenthesis.
    """
    return lexeme(string(')'))


def semicolon() -> Parser:
    """
    Parser that is accepting a semicolon.
    """
    return lexeme(string(';'))


def equals() -> Parser:
    """
    Parser that is accepting an equals sign.
    """
    return lexeme(string('='))


def quote() -> Parser:
    """
    Parser that is accepting a double quote.
    """
    return lexeme(string('\"'))


def key() -> Parser:
    """
    Parser consuming a key pattern.
    """
    return lexeme(regex(r'[A-Za-z][A-Za-z0-9_]*'))


def number() -> Parser:
    """
    Parser consuming a number pattern, and converting to float.
    """
    return lexeme(regex(r'[-\+]?(0|[1-9][0-9]*)([.][0-9]+)?([eE][+-]?[0-9]+)?')).map(float)


def remap(data: list) -> Dict[str, Any]:
    """
    Remap a parselist from .rpc and _rpc.txt, RPB has its custom
    remap.
    """
    rpc = dict()
    for key, value in data:
        rpc[key] = value

    # Reduce the coefficients to lists.
    for coeff in ['LINE_NUM_COEFF', 'LINE_DEN_COEFF',
                  'SAMP_NUM_COEFF',  'SAMP_DEN_COEFF']:
        values = list()
        for index in range(1, 21):
            key = f'{coeff}_{index}'
            values.append(rpc.pop(key))

        rpc[coeff] = values

    return rpc
