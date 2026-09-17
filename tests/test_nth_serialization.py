import pytest

from tinycss2 import nth


@pytest.mark.parametrize(('a', 'b', 'expected'), [
    (0, 0, '0'), (0, 1, '1'), (0, -2, '-2'),
    (1, 0, 'n'), (1, 3, 'n+3'), (1, -3, 'n-3'),
    (-1, 0, '-n'), (-1, 3, '-n+3'), (-1, -3, '-n-3'),
    (2, 0, '2n'), (2, 1, '2n+1'), (2, -4, '2n-4'),
    (-2, 0, '-2n'), (-2, 1, '-2n+1'), (-2, -4, '-2n-4'),
])
def test_serialize_nth(a, b, expected):
    # CSS Syntax's canonical form, including even/odd as 2n and 2n+1.
    assert nth.serialize_nth(a, b) == expected
    assert nth.parse_nth(expected) == (a, b)


@pytest.mark.parametrize('source', [
    'odd', 'even', '+n', '-n + 6', '3n - 2', '0n+5', 'n-0',
])
def test_serialize_parsed_nth(source):
    coefficients = nth.parse_nth(source)
    serialized = nth.serialize_nth(*coefficients)
    assert nth.parse_nth(serialized) == coefficients
    assert nth.serialize_nth(*nth.parse_nth(serialized)) == serialized


@pytest.mark.parametrize('a', [-1000, -1, 0, 1, 1000])
@pytest.mark.parametrize('b', [-1000, -1, 0, 1, 1000])
def test_serialize_nth_round_trip(a, b):
    assert nth.parse_nth(nth.serialize_nth(a, b)) == (a, b)
