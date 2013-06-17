import os.path
import json
import functools
import pprint

import pytest

from .tokenizer import tokenize
from .ast import (
    AtKeywordToken, CurlyBracketsBlock, DimensionToken, Function,
    HashToken, IdentToken, LiteralToken, NumberToken, ParenthesesBlock,
    ParseError, SquareBracketsBlock, StringToken, URLToken,
    UnicodeRangeToken, WhitespaceToken)


def generic(func):
    implementations = func()

    @functools.wraps(func)
    def run(value):
        return implementations[type(value)](value)
    return run


@generic
def component_value_to_json():
    numeric = lambda t: [
        t.representation, t.value,
        'integer' if t.int_value is not None else 'number']
    nested = lambda values: [component_value_to_json(v) for v in values]
    return {
        ParseError: lambda e: ['error', e.kind],
        WhitespaceToken: lambda t: ' ',
        LiteralToken: lambda t: t.value,
        IdentToken: lambda t: ['ident', t.value],
        AtKeywordToken: lambda t: ['at-keyword', t.value],
        HashToken: lambda t: ['hash', t.value,
                              'id' if t.is_identifier else 'unrestricted'],
        StringToken: lambda t: ['string', t.value],
        URLToken: lambda t: ['url', t.value],
        NumberToken: lambda t: ['number'] + numeric(t),
        DimensionToken: lambda t: (['dimension'] + numeric(t) + [t.unit]
                                   if t.unit != '%' else
                                   ['percentage'] + numeric(t)),
        UnicodeRangeToken: lambda t: ['unicode-range',
                                      list(t.range) if t.range else None],
        CurlyBracketsBlock: lambda t: ['{}'] + nested(t.content),
        SquareBracketsBlock: lambda t: ['[]'] + nested(t.content),
        ParenthesesBlock: lambda t: ['()'] + nested(t.content),
        Function: lambda t: ['function', t.name] + nested(t.arguments),
    }


def load_json(filename):
    loaded = json.load(open(os.path.join(
        os.path.dirname(__file__), 'tests', filename)))
    return list(zip(loaded[::2], loaded[1::2]))


@pytest.mark.parametrize(('css', 'expected'),
                         load_json('component_value_list.json'))
def test_tokenizer(css, expected):
    values = [component_value_to_json(t) for t in tokenize(css)]
    if values != expected:
        pprint.pprint(values)
        assert values == expected
