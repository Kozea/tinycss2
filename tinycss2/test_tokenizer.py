import os.path
import json

from .tokenizer import tokenize
from .tokens import *


TO_JSON = {
    WhitespaceToken: lambda t: ' ',
    BadStringToken: lambda t: t.type,
    BadURLToken: lambda t: t.type,
    LiteralToken: lambda t: t.value,
    SimpleToken: lambda t: (t.type, t.value),
    DimensionToken: lambda t: (
        t.type, t.value, t.representation, t.is_integer, t.unit),
    NumericToken: lambda t: (
        t.type, t.value, t.representation, t.is_integer),
    Block: lambda t: (t.type, to_json(t.conent)),
    Function: lambda t: (t.type, t.name, to_json(t.arguments)),
}


def to_json(tokens):
    results = []
    for token in tokens:
        for class_ in type(token).mro():
            implementation = TO_JSON.get(class_)
            if implementation:
                results.append(implementation(token))
                break
        else:
            assert TypeError(token)
    return results


def run_tests():
    for test in json.load(open(os.path.join(
            os.path.dirname(__file__), 'tokenizer_tests.json'))):
        assert tokenize(test['css']) == test['tokens'], test.get('comment')
