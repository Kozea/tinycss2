import os.path
import json
import functools
import pprint

import pytest

from . import (
    parse_component_value_list, parse_one_component_value,
    parse_one_declaration)
from .ast import (
    AtKeywordToken, CurlyBracketsBlock, DimensionToken, Function,
    HashToken, IdentToken, LiteralToken, NumberToken, ParenthesesBlock,
    ParseError, PercentageToken, SquareBracketsBlock, StringToken, URLToken,
    UnicodeRangeToken, WhitespaceToken, Declaration)


def generic(func):
    implementations = func()

    @functools.wraps(func)
    def run(value):
        return implementations[type(value)](value)
    return run


@generic
def to_json():
    numeric = lambda t: [
        t.representation, t.value,
        'integer' if t.int_value is not None else 'number']
    return {
        list: lambda l: [to_json(el) for el in l],
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
        PercentageToken: lambda t: ['percentage'] + numeric(t),
        DimensionToken: lambda t: ['dimension'] + numeric(t) + [t.unit],
        UnicodeRangeToken: lambda t: ['unicode-range',
                                      list(t.range) if t.range else None],

        CurlyBracketsBlock: lambda t: ['{}'] + to_json(t.content),
        SquareBracketsBlock: lambda t: ['[]'] + to_json(t.content),
        ParenthesesBlock: lambda t: ['()'] + to_json(t.content),
        Function: lambda t: ['function', t.name] + to_json(t.arguments),

        Declaration: lambda d: [d.name, to_json(d.value), d.important],
    }


def json_test(filename):
    def decorator(function):
        json_data = json.load(open(os.path.join(
            os.path.dirname(__file__), 'tests', filename)))
        json_data = list(zip(json_data[::2], json_data[1::2]))

        @pytest.mark.parametrize(('css', 'expected'), json_data)
        def test(css, expected):
            value = function(css)
            if value != expected:  # pragma: no cover
                pprint.pprint(value)
                assert value == expected
        return test
    return decorator


@json_test('component_value_list.json')
def test_component_value_list(css):
    return [to_json(t) for t in parse_component_value_list(css)]


@json_test('one_component_value.json')
def test_one_component_value(css):
    return to_json(parse_one_component_value(css))


@json_test('one_declaration.json')
def test_one_declaration(css):
    return to_json(parse_one_declaration(css))
