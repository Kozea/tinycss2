import os.path
import json
import pprint
import functools

from .tokenizer import tokenize
from .ast import WhitespaceToken, LiteralToken


def generic(func):
    implementations = func()

    @functools.wraps(func)
    def run(value):
        return implementations[type(value)](value)
    return run


@generic
def component_value_to_json():
    return {
        WhitespaceToken: lambda t: ' ',
        LiteralToken: lambda t: t.value,
    }


def test_tokenizer():
    for comment, css, expected in json.load(open(os.path.join(
            os.path.dirname(__file__), 'tests/component_values.json'))):
        values = [component_value_to_json(t) for t in tokenize(css)]
        if values != expected:
            pprint.pprint(values)
            print('!=')
            pprint.pprint(expected)
            assert 0, comment
