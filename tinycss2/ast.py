# coding: utf8
"""

Data structures for the CSS abstract syntax tree.

Differences with css-syntax:

* :class:`LiteralToken` regroups
  colon ``:``, semicolon ``;``, comma ``,``, cdo ``<!--``, cdc ``-->``,
  include-match ``~=``, dash-match ``|=``,
  prefix-match ``^=``, suffix-match ``$=``, substring-match ``*=``,
  and delim tokens.
  (Delim is any single character not matched by another token.)

"""

from __future__ import unicode_literals

from .utils import ascii_lower


class Node(object):
    """Base class for all tokens.

    .. attribute:: source_line

        The line number of the start of the node in the CSS source.

    .. attribute:: source_column

        The column number within :attr:`line` of the start of the node
        in the CSS source.

    """
    __slots__ = ['source_line', 'source_column']

    def __init__(self, source_line, source_column):
        self.source_line = source_line
        self.source_column = source_column


class ParseError(Node):
    """A syntax error of some sort.

    .. attribute:: kind

        Machine-readable string indicating the type of error.
        Example: ``'bad-url'``.

    .. attribute:: message

        Human-readable explanation of the error, as a string.
        Could be translated, expanded to include details, etc.

    """
    __slots__ = ['kind', 'message']
    type = 'error'

    def __init__(self, line, column, kind, message):
        Node.__init__(self, line, column)
        self.kind = kind
        self.message = message


class Comment(Node):
    """A CSS comment."""
    __slots__ = ['value']
    type = 'comment'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value


class WhitespaceToken(Node):
    """A <whitespace> token."""
    __slots__ = []
    type = 'whitespace'


class LiteralToken(Node):
    r"""Token that represents one or more characters as in the CSS source.

    .. attribute:: value

        A string of one to four characters.

    Instances compare equal to their value.

    This regroups what the spec defines as
    <delim>, <colon>, <semicolon>, <comma>, <cdc>, <cdo>,
    <include-match>, <dash-match>, <prefix-match>, <suffix-match>,
    and <substring-match> tokens.

    """
    __slots__ = ['value']
    type = 'literal'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value

    def __eq__(self, other):
        return self.value == other or self is other

    def __ne__(self, other):
        return not self == other


class IdentToken(Node):
    """A <ident> token.

    .. attribute:: value

        The unescaped value, as an Unicode string.

    .. attribute:: lower_value

        Same as :attr:`value` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to a CSS keyword.

    """
    __slots__ = ['value', 'lower_value']
    type = 'ident'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value
        self.lower_value = ascii_lower(value)


class AtKeywordToken(Node):
    """A <at-keyword> token.

    .. attribute:: value

        The unescaped value, as an Unicode string.

    .. attribute:: lower_value

        Same as :attr:`value` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to a CSS at-keyword.

    """
    __slots__ = ['value', 'lower_value']
    type = 'at-keyword'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value
        self.lower_value = ascii_lower(value)


class HashToken(Node):
    r"""A <hash> token.

    .. attribute:: value

        The unescaped value, as an Unicode string.

    .. attribute:: is_identifier

        A :class:`bool`, true if the CSS source for this token
        was ``#`` followed by a valid identifier.
        (Only such hash tokens are valid ID selectors.)

    """
    __slots__ = ['value', 'is_identifier']
    type = 'hash'

    def __init__(self, line, column, value, is_identifier):
        Node.__init__(self, line, column)
        self.value = value
        self.is_identifier = is_identifier


class StringToken(Node):
    """A <string> token.

    .. attribute:: value

        The unescaped value, as an Unicode string, without the quotes.

    """
    __slots__ = ['value']
    type = 'string'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value


class URLToken(Node):
    """A <url> token.

    .. attribute:: value

        The unescaped URL, as an Unicode string,
        without the ``url(`` and ``)`` markers or the optional quotes.

    """
    __slots__ = ['value']
    type = 'url'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value


class UnicodeRangeToken(Node):
    """An <unicode-range> token.

    .. attribute:: range

        A ``(start, end)`` tuple of Unicode characters for an inclusive range,
        or ``None`` for empty ranges.

    """
    __slots__ = ['range']
    type = 'unicode-range'

    def __init__(self, line, column, range_):
        Node.__init__(self, line, column)
        self.range = range_


class NumberToken(Node):
    """A <number> token.

    .. attribute:: value

        The numeric value as a :class:`float`.

    .. attribute:: int_value

        The numeric value as an :class:`int`
        if :attr:`is_integer` is true, :obj:`None` otherwise.

    .. attribute:: is_integer

        Whether the token was syntactically an integer, as a boolean.

    .. attribute:: representation

        The CSS representation of the value, as an Unicode string.

    """
    __slots__ = ['value', 'int_value', 'is_integer', 'representation']
    type = 'number'

    def __init__(self, line, column, value, int_value, representation):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.is_integer = int_value is not None
        self.representation = representation


class PercentageToken(Node):
    """A <percentage> token.

    .. attribute:: value

        The value numeric as a :class:`float`.

    .. attribute:: int_value

        The numeric value as an :class:`int`
        if the token was syntactically an integer,
        or :obj:`None`.

    .. attribute:: representation

        The CSS representation of the value without the unit,
        as an Unicode string.

    """
    __slots__ = ['value', 'int_value', 'representation']
    type = 'percentage'

    def __init__(self, line, column, value, int_value, representation):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.representation = representation


class DimensionToken(Node):
    """A <dimension> token.

    .. attribute:: value

        The value numeric as a :class:`float`.

    .. attribute:: int_value

        The numeric value as an :class:`int`
        if the token was syntactically an integer,
        or :obj:`None`.

    .. attribute:: representation

        The CSS representation of the value without the unit,
        as an Unicode string.

    .. attribute:: unit

        The unescaped unit, as an Unicode string.

    .. attribute:: lower_unit

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to a CSS unit.

    """
    __slots__ = ['value', 'int_value', 'representation', 'unit', 'lower_unit']
    type = 'dimension'

    def __init__(self, line, column, value, int_value, representation, unit):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.representation = representation
        self.unit = unit
        self.lower_unit = ascii_lower(unit)


class ParenthesesBlock(Node):
    """A () block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '() block'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content


class SquareBracketsBlock(Node):
    """A [] block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '[] block'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content


class CurlyBracketsBlock(Node):
    """A {} block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '{} block'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content


class Function(Node):
    """A CSS function.

    .. attribute:: name

        The unescaped name of the function, as an Unicode string.

    .. attribute:: lower_name

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to a CSS function name.

    .. attribute:: arguments

        The arguments of the function, as list of :ref:`component values`.
        The ``(`` and ``)`` markers themselves are not represented in the list.
        Commas are not special, but represented as :obj:`LiteralToken` objects
        in the list.

    """
    __slots__ = ['name', 'lower_name', 'arguments']
    type = 'function'

    def __init__(self, line, column, name, arguments):
        Node.__init__(self, line, column)
        self.name = name
        self.lower_name = ascii_lower(name)
        self.arguments = arguments


class Declaration(Node):
    """A (property or descriptor) declaration.

    Syntax:
    ``<ident> <whitespace>* ':' <token>* ( '!' <ident("important")> )?``

    .. attribute:: name

        The unescaped value, as an Unicode string.

    .. attribute:: lower_name

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to
        a CSS property or descriptor name.

    .. attribute:: value

        The declaration value as a list of :ref:`component values`:
        anything between ``:`` and
        the end of the declaration, or ``!important``.

    .. attribute:: important

        A boolean, true if the declaration had an ``!important`` markers.
        It is up to the consumer to reject declarations that do not accept
        this flag, such as non-property descriptor declarations.

    """
    __slots__ = ['name', 'lower_name', 'value', 'important']
    type = 'declaration'

    def __init__(self, line, column, name, lower_name, value, important):
        Node.__init__(self, line, column)
        self.name = name
        self.lower_name = lower_name
        self.value = value
        self.important = important


class QualifiedRule(Node):
    """A qualified rule, ie. a rule that is not an at-rule.

    Qulified rules are often style rules,
    where the prelude is parsed as a selector list
    and the content as a declaration list.

    Syntax:
    ``<token except {} block>* <{} block>``

    .. attribute:: prelude

        The rule’s prelude, the part before the {} block,
        as a list of :ref:`component values`.

    .. attribute:: content

        The rule’s content, the part inside the {} block,
        as a list of :ref:`component values`.

    """
    __slots__ = ['prelude', 'content']
    type = 'qualified-rule'

    def __init__(self, line, column, prelude, content):
        Node.__init__(self, line, column)
        self.prelude = prelude
        self.content = content


class AtRule(Node):
    """An at-rule.

    The interpretation of at-rules depend on their at-keywords.
    Most at-rules (ie. at-keyword values) are only allowed in some context,
    and must either end with a {} block or a semicolon.

    Syntax:
    ``<at-keyword> <token except {} block>* ( <{} block> | ';' )``

    .. attribute:: at_keyword

        The unescaped value of the rule’s at-keyword,
        without the ``@`` symbol, as an Unicode string.

    .. attribute:: lower_at_keyword

        Same as :attr:`at_keyword` but normalized to *ASCII lower case*,
        see :func:`~tinycss2.ascii_lower`.
        This is the value to use when comparing to a CSS at-keyword.

    .. attribute:: prelude

        The rule’s prelude, the part before the {} block or semicolon,
        as a list of :ref:`component values`.

    .. attribute:: content

        The rule’s content, if any.
        The block’s content as a list of :ref:`component values`
        for at-rules with a {} block,
        or :obj:`None` for at-rules ending with a semicolon.

    """
    __slots__ = ['at_keyword', 'lower_at_keyword', 'prelude', 'content']
    type = 'at-rule'

    def __init__(self, line, column,
                 at_keyword, lower_at_keyword, prelude, content):
        Node.__init__(self, line, column)
        self.at_keyword = at_keyword
        self.lower_at_keyword = lower_at_keyword
        self.prelude = prelude
        self.content = content
