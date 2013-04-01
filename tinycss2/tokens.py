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


class Token(object):
    """Base class for all tokens."""
    __slots__ = []


class WhitespaceToken(Token):
    """The whitespace token.

    Has no instance attribute, so a singleton can be used.
    Instances compare equal to the  ``' '`` string made of exactly one space.

    """
    __slots__ = []
    type = 'whitespace'

    def __eq__(self, other):
        return other == ' ' or Token.__eq__(self, other)

    def __ne__(self, other):
        return not self == other


class SimpleToken(Token):
    """Base class for tokens with a single ``value`` attribute."""
    __slots__ = ['value']

    def __init__(self, value):
        self.value = value


# Delim, colon, semicolon, comma, cdc, cdo,
# include-match, dash-match, prefix-match, suffix-match, substring-match.
class LiteralToken(SimpleToken):
    r"""Token that reprensents one or more characters as in the CSS source.

    .. attribute:: value

        A string of one to four characters.

    Instances compare equal to their value.

    """
    __slots__ = []
    type = 'literal'

    def __eq__(self, other):
        return self.value == other or SimpleToken.__eq__(self, other)

    def __ne__(self, other):
        return not self == other


class IdentToken(SimpleToken):
    """A CSS identifier token.

    .. attribute:: value

        The unescaped string, as an Unicode string.

    """
    __slots__ = []
    type = 'ident'


class AtKeywordToken(SimpleToken):
    """A CSS at-keyword token.

    .. attribute:: value

        The unescaped string, as an Unicode string, without the ``@`` symbol.

    """
    __slots__ = []
    type = 'at-keyword'


class HashToken(SimpleToken):
    """A CSS hash token.

    .. attribute:: value

        The unescaped string, as an Unicode string, without the ``#`` symbol.

    """
    __slots__ = []
    type = 'hash'


class StringToken(SimpleToken):
    """A quoted string token.

    .. attribute:: value

        The unescaped string, as an Unicode string, without the quotes.

    """
    __slots__ = []
    type = 'string'


class URLToken(SimpleToken):
    """A CSS url() token.

    .. attribute:: value

        The unescaped URL, as an Unicode string,
        without the ``url(`` and ``)`` markers or the optional quotes.

    """
    __slots__ = []
    type = 'url'


class UnicodeRangeToken(SimpleToken):
    """An unicode-range token. Represents a range of characters.

    .. attribute:: value

        A ``(start, end)`` inclusive tuple of (integer) codepoints,
        or ``None`` for empty ranges.

    """
    __slots__ = []
    type = 'unicode-range'


class NumericToken(SimpleToken):
    """Base class for tokens with a numeric value."""
    __slots__ = ['representation', 'is_integer']

    def __init__(self, value, representation, is_integer):
        SimpleToken.__init__(self, value)
        self.representation = representation
        self.is_integer = is_integer


class NumberToken(NumericToken):
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


class DimensionToken(NumericToken):
    """A number token.

    .. attribute:: value

        The value as a :class:`float` or an :class:`int`,
        depending on :attr:`is_integer`

    .. attribute:: representation

        The CSS representation of the value, as an Unicode string.

    .. attribute:: is_integer

        A boolean, true if the representation matches the integer syntax.
        (ie. no ``.`` decimal point, no scientific notation.)

    .. attribute:: unit

        The unescaped unit, as an Unicode string.
        Either ``%`` or an identifier such as ``px``.

    """
    __slots__ = ['unit']
    type = 'dimension'

    def __init__(self, value, representation, is_integer, unit):
        NumericToken.__init__(self, value, representation, is_integer)
        self.unit = unit


class BadStringToken(Token):
    """The bad-string token.

    Has no instance attribute, so a singleton can be used.

    """
    __slots__ = []
    type = 'bad-string'


class BadURLToken(Token):
    """The bad-url token.

    Has no instance attribute, so a singleton can be used.

    """
    __slots__ = []
    type = 'bad-url'


class Block(Token):
    """Base class for (), [] and {} blocks."""
    __slots__ = ['content']

    def __init__(self, content):
        self.content = content


class ParenthesesBlock(Block):
    """A () block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    type = '() block'


class SquareBracketsBlock(Block):
    """A [] block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    type = '[] block'


class CurlyBracketsBlock(Block):
    """A {} block.

    .. attribute:: content

        The content of the block, as list of tokens.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    type = '{} block'


class Function(Token):
    """A CSS function.

    .. attribute:: name

        The unescaped name of the function, as an Unicode string.

    .. attribute:: content

        The arguments of the function, as list of tokens.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    __slots__ = ['name', 'arguments']
    type = 'function'

    def __init__(self, name, arguments):
        self.name = name
        self.arguments = arguments


WHITESPACE_TOKEN = WhitespaceToken()
BAD_STRING_TOKEN = BadStringToken()
BAD_URL_TOKEN = BadURLToken()
CDO_TOKEN = LiteralToken('<--')
CDC_TOKEN = LiteralToken('-->')
ATTRIBUTE_OPERATOR_TOKENS = dict((c, LiteralToken(c + '=')) for c in '~|^$*')
# Not all of these are ever used, but don’t bother.
DELIM_TOKENS = dict((c, LiteralToken(c)) for c in map(chr, range(128)))
