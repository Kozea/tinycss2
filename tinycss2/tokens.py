"""

Data structures representing tokens, blocks, and functions.

Differences with css-syntax:

* :class:`DimensionToken` also includes percentage tokens,
  which have ``'%'`` as their :attr:`~DimensionToken.unit` attribute.
* :class:`LiteralToken` regroups
  colon ``:``, semicolon ``;``, comma ``,``, cdo ``<!--``, cdc ``-->``,
  include-match ``~=``, dash-match ``|=``,
  prefix-match ``^=``, suffix-match ``$=``, substring-match ``*=``,
  and delim tokens.
  (Delim is any single character not matched by another token.)

"""

from __future__ import unicode_literals

from . import ascii_lower


class _Token(object):
    """Base class for all tokens."""
    __slots__ = ['source_line', 'source_column']

    def __init__(self, line, column):
        self.source_line = line
        self.source_column = column


class WhitespaceToken(_Token):
    """A whitespace token."""
    __slots__ = []
    type = 'whitespace'


# Delim, colon, semicolon, comma, cdc, cdo,
# include-match, dash-match, prefix-match, suffix-match, substring-match.
class LiteralToken(_Token):
    r"""Token that reprensents one or more characters as in the CSS source.

    .. attribute:: value

        A string of one to four characters.

    Instances compare equal to their value.

    """
    __slots__ = ['value']
    type = 'literal'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = value

    def __eq__(self, other):
        return self.value == other or _Token.__eq__(self, other)

    def __ne__(self, other):
        return not self == other


class IdentToken(_Token):
    """A CSS identifier token.

    .. attribute:: value

        The unescaped value, as an Unicode string.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_value

        Same as :attr:`value`, but with the original casing preserved.

    """
    __slots__ = ['value', 'case_sensitive_value']
    type = 'ident'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = ascii_lower(value)
        self.case_sensitive_value = value


class AtKeywordToken(_Token):
    """A CSS at-keyword token.

    .. attribute:: value

        The unescaped value, as an Unicode string, without the ``@`` symbol.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_value

        Same as :attr:`value`, but with the original casing preserved.

    """
    __slots__ = ['value', 'case_sensitive_value']
    type = 'at-keyword'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = ascii_lower(value)
        self.case_sensitive_value = value


class HashToken(_Token):
    """A CSS hash token.

    .. attribute:: value

        The unescaped string, as an Unicode string, without the ``#`` symbol.
        The original casing is preserved.

    """
    __slots__ = ['value']
    type = 'hash'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = value


class StringToken(_Token):
    """A quoted string token.

    .. attribute:: value

        The unescaped string, as an Unicode string, without the quotes.
        The original casing is preserved.

    """
    __slots__ = ['value']
    type = 'string'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = value


class URLToken(_Token):
    """A CSS url() token.

    .. attribute:: value

        The unescaped URL, as an Unicode string,
        without the ``url(`` and ``)`` markers or the optional quotes.
        The original casing is preserved.

    """
    __slots__ = ['value']
    type = 'url'

    def __init__(self, line, column, value):
        _Token.__init__(self, line, column)
        self.value = value


class UnicodeRangeToken(_Token):
    """An unicode-range token. Represents a range of characters.

    .. attribute:: range

        A ``(start, end)`` tuple of Unicode characters for an inclusive range,
        or ``None`` for empty ranges.

    """
    __slots__ = ['range']
    type = 'unicode-range'

    def __init__(self, line, column, range_):
        _Token.__init__(self, line, column)
        self.range = range_


class _NumericToken(_Token):
    """Base class for tokens with a numeric value."""
    __slots__ = ['value', 'representation', 'is_integer']

    def __init__(self, line, column, value, representation, is_integer):
        _Token.__init__(self, line, column)
        self.value = value
        self.representation = representation
        self.is_integer = is_integer


class NumberToken(_NumericToken):
    """A number token.

    .. attribute:: value

        The value as an :class:`int` if :attr:`is_integer` is true,
        as a :class:`float` otherwise.

    .. attribute:: representation

        The CSS representation of the value, as an Unicode string.

    .. attribute:: is_integer

        A boolean, true if the representation matches the integer syntax.
        (ie. no ``.`` decimal point, no scientific notation.)

    """
    __slots__ = []
    type = 'number'


class DimensionToken(_NumericToken):
    """A dimension token (number followed by an unit.)

    .. attribute:: value

        The value as a :class:`float` or an :class:`int`,
        depending on :attr:`is_integer`

    .. attribute:: representation

        The CSS representation of the value without the unit,
        as an Unicode string.

    .. attribute:: is_integer

        A boolean, true if the representation matches the integer syntax.
        (ie. no ``.`` decimal point, no scientific notation.)

    .. attribute:: unit

        The unescaped unit, as an Unicode string.
        Either ``%`` or an identifier such as ``px``.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_unit

        Same as :attr:`unit`, but with the original casing preserved.

    """
    __slots__ = ['unit', 'case_sensitive_unit']
    type = 'dimension'

    def __init__(self, line, column, value, representation, is_integer, unit):
        _NumericToken.__init__(
            self, line, column, value, representation, is_integer)
        self.unit = ascii_lower(unit)
        self.case_sensitive_unit = unit


class BadStringToken(_Token):
    """A bad-string token. Always a parse error."""
    __slots__ = []
    type = 'bad-string'


class BadURLToken(_Token):
    """A bad-url token. Always a parse error."""
    __slots__ = []
    type = 'bad-url'


class _Block(_Token):
    """Base class for (), [] and {} blocks."""
    __slots__ = ['content']

    def __init__(self, line, column, content):
        _Token.__init__(self, line, column)
        self.content = content


class ParenthesesBlock(_Block):
    """A () block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    type = '() block'


class SquareBracketsBlock(_Block):
    """A [] block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    type = '[] block'


class CurlyBracketsBlock(_Block):
    """A {} block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    type = '{} block'


class Function(_Token):
    """A CSS function.

    .. attribute:: name

        The unescaped name of the function, as an Unicode string.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_name

        Same as :attr:`name`, but with the original casing preserved.

    .. attribute:: content

        The arguments of the function, as list of tokens.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    __slots__ = ['name', 'case_sensitive_name', 'arguments']
    type = 'function'

    def __init__(self, line, column, name, arguments):
        _Token.__init__(self, line, column)
        self.name = ascii_lower(name)
        self.case_sensitive_name = name
        self.arguments = arguments
