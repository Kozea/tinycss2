import os.path
import json
import functools
import pprint

import pytest
from webencodings import Encoding, lookup

from . import (
    parse_component_value_list, parse_one_component_value,
    parse_declaration_list, parse_one_declaration,
    parse_rule_list, parse_one_rule, parse_stylesheet, parse_stylesheet_bytes,
    serialize)
from .ast import (
    AtKeywordToken, CurlyBracketsBlock, DimensionToken, FunctionBlock,
    HashToken, IdentToken, LiteralToken, NumberToken, ParenthesesBlock,
    ParseError, PercentageToken, SquareBracketsBlock, StringToken, URLToken,
    UnicodeRangeToken, WhitespaceToken, Declaration, AtRule, QualifiedRule)
from .color3 import parse_color, RGBA
from .nth import parse_nth


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
        type(None): lambda _: None,
        str: lambda s: s,
        int: lambda s: s,
        list: lambda l: [to_json(el) for el in l],
        tuple: lambda l: [to_json(el) for el in l],
        Encoding: lambda e: e.name,
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
        UnicodeRangeToken: lambda t: ['unicode-range', t.start, t.end],

        CurlyBracketsBlock: lambda t: ['{}'] + to_json(t.content),
        SquareBracketsBlock: lambda t: ['[]'] + to_json(t.content),
        ParenthesesBlock: lambda t: ['()'] + to_json(t.content),
        FunctionBlock: lambda t: ['function', t.name] + to_json(t.arguments),

        Declaration: lambda d: ['declaration', d.name,
                                to_json(d.value), d.important],
        AtRule: lambda r: ['at-rule', r.at_keyword, to_json(r.prelude),
                           to_json(r.content)],
        QualifiedRule: lambda r: ['qualified rule', to_json(r.prelude),
                                  to_json(r.content)],

        RGBA: lambda v: [round(c, 10) for c in v],
    }


def load_json(filename):
    json_data = json.load(open(os.path.join(
        os.path.dirname(__file__), 'css-parsing-tests', filename)))
    return list(zip(json_data[::2], json_data[1::2]))


def json_test(function, filename=None):
    filename = filename or function.__name__.split('_', 1)[-1] + '.json'

    @pytest.mark.parametrize(('css', 'expected'), load_json(filename))
    def test(css, expected):
        result = function(css)
        repr(result)  # Test that these do not raise
        value = to_json(result)
        if value != expected:  # pragma: no cover
            pprint.pprint(value)
            assert value == expected
    return test


test_component_value_list = json_test(parse_component_value_list)
test_one_component_value = json_test(parse_one_component_value)
test_declaration_list = json_test(parse_declaration_list)
test_one_declaration = json_test(parse_one_declaration)
test_stylesheet = json_test(parse_stylesheet)
test_rule_list = json_test(parse_rule_list)
test_one_rule = json_test(parse_one_rule)
test_color3 = json_test(parse_color, filename='color3.json')
test_nth = json_test(parse_nth, filename='An+B.json')


# Do not use @pytest.mark.parametrize because it is slow with that many values.
def test_color3_hsl():
    for css, expected in load_json('color3_hsl.json'):
        assert to_json(parse_color(css)) == expected


def test_color3_keywords():
    for css, expected in load_json('color3_keywords.json'):
        result = parse_color(css)
        if result is not None:
            r, g, b, a = result
            result = [r * 255, g * 255, b * 255, a]
        assert result == expected


@json_test
def test_stylesheet_bytes(kwargs):
    kwargs['css_bytes'] = kwargs['css_bytes'].encode('latin1')
    kwargs.pop('comment', None)
    if kwargs.get('environment_encoding'):
        kwargs['environment_encoding'] = lookup(kwargs['environment_encoding'])
    return parse_stylesheet_bytes(**kwargs)


def test_serialization(css):
    parsed = parse_component_value_list(css)
    return parse_component_value_list(serialize(parsed))

test_serialization = json_test(test_serialization, 'component_value_list.json')
