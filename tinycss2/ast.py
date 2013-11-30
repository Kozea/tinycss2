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

from webencodings import ascii_lower

from .serializer import (serialize_identifier, serialize_name,
                         serialize_string_value, _serialize_to)


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

    def __repr__(self):
        return self.repr_format.format(self=self)

    def serialize(self):
        """Serialize this node to CSS syntax and return an Unicode string."""
        chuncks = []
        self._serialize_to(chuncks.append)
        return ''.join(chuncks)

    def _serialize_to(self, write):
        """Serialize this node to CSS syntax, writing chuncks as Unicode string
        by calling the provided :obj:`write` callback.

        """
        raise NotImplementedError


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
    repr_format = '<{self.__class__.__name__} {self.kind}>'

    def __init__(self, line, column, kind, message):
        Node.__init__(self, line, column)
        self.kind = kind
        self.message = message

    def _serialize_to(self, write):
        if self.kind == 'bad-string':
            write('"[bad string]\n')
        elif self.kind == 'bad-url':
            write('url([bad url])')
        elif self.kind in ')]}':
            write(self.kind)
        else:
            raise TypeError('Can not serialize %r' % self)



class Comment(Node):
    """A CSS comment."""
    __slots__ = ['value']
    type = 'comment'
    repr_format = '<{self.__class__.__name__} {self.value:r}>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value

    def _serialize_to(self, write):
        write('/*')
        write(self.value)
        write('*/')


class WhitespaceToken(Node):
    """A <whitespace> token."""
    __slots__ = []
    type = 'whitespace'
    repr_format = '<{self.__class__.__name__}>'

    def _serialize_to(self, write):
        write(' ')


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
    repr_format = '<{self.__class__.__name__} {self.value}>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value

    def __eq__(self, other):
        return self.value == other or self is other

    def __ne__(self, other):
        return not self == other

    def _serialize_to(self, write):
        write(self.value)


class IdentToken(Node):
    """A <ident> token.

    .. attribute:: value

        The unescaped value, as an Unicode string.

    .. attribute:: lower_value

        Same as :attr:`value` but normalized to *ASCII lower case*,
        see :func:`~webencodings.ascii_lower`.
        This is the value to use when comparing to a CSS keyword.

    """
    __slots__ = ['value', 'lower_value']
    type = 'ident'
    repr_format = '<{self.__class__.__name__} {self.value}>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value
        self.lower_value = ascii_lower(value)

    def _serialize_to(self, write):
        write(serialize_identifier(self.value))


class AtKeywordToken(Node):
    """A <at-keyword> token.

    .. attribute:: value

        The unescaped value, as an Unicode string.

    .. attribute:: lower_value

        Same as :attr:`value` but normalized to *ASCII lower case*,
        see :func:`~webencodings.ascii_lower`.
        This is the value to use when comparing to a CSS at-keyword.

    """
    __slots__ = ['value', 'lower_value']
    type = 'at-keyword'
    repr_format = '<{self.__class__.__name__} @{self.value}>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value
        self.lower_value = ascii_lower(value)

    def _serialize_to(self, write):
        write('@')
        write(serialize_identifier(self.value))


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
    repr_format = '<{self.__class__.__name__} #{self.value}>'

    def __init__(self, line, column, value, is_identifier):
        Node.__init__(self, line, column)
        self.value = value
        self.is_identifier = is_identifier

    def _serialize_to(self, write):
        write('#')
        if self.is_identifier:
            write(serialize_identifier(self.value))
        else:
            write(serialize_name(self.value))


class StringToken(Node):
    """A <string> token.

    .. attribute:: value

        The unescaped value, as an Unicode string, without the quotes.

    """
    __slots__ = ['value']
    type = 'string'
    repr_format = '<{self.__class__.__name__} {self.value:r}>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value

    def _serialize_to(self, write):
        write('"')
        write(serialize_string_value(self.value))
        write('"')


class URLToken(Node):
    """A <url> token.

    .. attribute:: value

        The unescaped URL, as an Unicode string,
        without the ``url(`` and ``)`` markers or the optional quotes.

    """
    __slots__ = ['value']
    type = 'url'
    repr_format = '<{self.__class__.__name__} url({self.value})>'

    def __init__(self, line, column, value):
        Node.__init__(self, line, column)
        self.value = value

    def _serialize_to(self, write):
        write('url("')
        write(serialize_string_value(self.value))
        write('")')


class UnicodeRangeToken(Node):
    """An <unicode-range> token.

    .. attribute:: start

        The start of the range, as an integer.

    .. attribute:: end

        The end of the range, as an integer.

    """
    __slots__ = ['start', 'end']
    type = 'unicode-range'
    repr_format = '<{self.__class__.__name__} {self.start} {self.end}>'

    def __init__(self, line, column, start, end):
        Node.__init__(self, line, column)
        self.start = start
        self.end = end

    def _serialize_to(self, write):
        if self.end == self.start:
            write('U+%X' % self.start)
        else:
            write('U+%X-%X' % (self.start, self.end))


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
    repr_format = '<{self.__class__.__name__} {self.representation}>'

    def __init__(self, line, column, value, int_value, representation):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.is_integer = int_value is not None
        self.representation = representation

    def _serialize_to(self, write):
        write(self.representation)


class PercentageToken(Node):
    """A <percentage> token.

    .. attribute:: value

        The value numeric as a :class:`float`.

    .. attribute:: int_value

        The numeric value as an :class:`int`
        if the token was syntactically an integer,
        or :obj:`None`.

    .. attribute:: is_integer

        Whether the token’s value was syntactically an integer, as a boolean.

    .. attribute:: representation

        The CSS representation of the value without the unit,
        as an Unicode string.

    """
    __slots__ = ['value', 'int_value', 'is_integer', 'representation']
    type = 'percentage'
    repr_format = '<{self.__class__.__name__} {self.representation}%>'

    def __init__(self, line, column, value, int_value, representation):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.is_integer = int_value is not None
        self.representation = representation

    def _serialize_to(self, write):
        write(self.representation)
        write('%')


class DimensionToken(Node):
    """A <dimension> token.

    .. attribute:: value

        The value numeric as a :class:`float`.

    .. attribute:: int_value

        The numeric value as an :class:`int`
        if the token was syntactically an integer,
        or :obj:`None`.

    .. attribute:: is_integer

        Whether the token’value was syntactically an integer, as a boolean.

    .. attribute:: representation

        The CSS representation of the value without the unit,
        as an Unicode string.

    .. attribute:: unit

        The unescaped unit, as an Unicode string.

    .. attribute:: lower_unit

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~webencodings.ascii_lower`.
        This is the value to use when comparing to a CSS unit.

    """
    __slots__ = ['value', 'int_value', 'is_integer', 'representation',
                 'unit', 'lower_unit']
    type = 'dimension'
    repr_format = '<{self.__class__.__name__} {self.representation}{self.unit}>'

    def __init__(self, line, column, value, int_value, representation, unit):
        Node.__init__(self, line, column)
        self.value = value
        self.int_value = int_value
        self.is_integer = int_value is not None
        self.representation = representation
        self.unit = unit
        self.lower_unit = ascii_lower(unit)

    def _serialize_to(self, write):
        write(self.representation)
        # Disambiguate with scientific notation
        unit = self.unit
        if unit in ('e', 'E') or unit.startswith(('e-', 'E-')):
            write('\\65 ')
            write(serialize_name(unit[1:]))
        else:
            write(serialize_identifier(unit))


class ParenthesesBlock(Node):
    """A () block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``(`` and ``)`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '() block'
    repr_format = '<{self.__class__.__name__} ( {self.content} )>'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content

    def _serialize_to(self, write):
        write('(')
        _serialize_to(self.content, write)
        write(')')


class SquareBracketsBlock(Node):
    """A [] block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '[] block'
    repr_format = '<{self.__class__.__name__} [ {self.content} ]>'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content

    def _serialize_to(self, write):
        write('[')
        _serialize_to(self.content, write)
        write(']')


class CurlyBracketsBlock(Node):
    """A {} block.

    .. attribute:: content

        The content of the block, as list of :ref:`component values`.
        The ``[`` and ``]`` markers themselves are not represented in the list.

    """
    __slots__ = ['content']
    type = '{} block'
    repr_format = '<{self.__class__.__name__} {{ {self.content} }}>'

    def __init__(self, line, column, content):
        Node.__init__(self, line, column)
        self.content = content

    def _serialize_to(self, write):
        write('{')
        _serialize_to(self.content, write)
        write('}')


class Function(Node):
    """A CSS function.

    .. attribute:: name

        The unescaped name of the function, as an Unicode string.

    .. attribute:: lower_name

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~webencodings.ascii_lower`.
        This is the value to use when comparing to a CSS function name.

    .. attribute:: arguments

        The arguments of the function, as list of :ref:`component values`.
        The ``(`` and ``)`` markers themselves are not represented in the list.
        Commas are not special, but represented as :obj:`LiteralToken` objects
        in the list.

    """
    __slots__ = ['name', 'lower_name', 'arguments']
    type = 'function'
    repr_format = '<{self.__class__.__name__} {self.name}( {self.arguments} )>'

    def __init__(self, line, column, name, arguments):
        Node.__init__(self, line, column)
        self.name = name
        self.lower_name = ascii_lower(name)
        self.arguments = arguments

    def _serialize_to(self, write):
        write(serialize_identifier(self.name))
        write('(')
        _serialize_to(self.arguments, write)
        write(')')


class Declaration(Node):
    """A (property or descriptor) declaration.

    Syntax:
    ``<ident> <whitespace>* ':' <token>* ( '!' <ident("important")> )?``

    .. attribute:: name

        The unescaped value, as an Unicode string.

    .. attribute:: lower_name

        Same as :attr:`name` but normalized to *ASCII lower case*,
        see :func:`~webencodings.ascii_lower`.
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
    repr_format = '<{self.__class__.__name__} {self.name}: {self.value}>'

    def __init__(self, line, column, name, lower_name, value, important):
        Node.__init__(self, line, column)
        self.name = name
        self.lower_name = lower_name
        self.value = value
        self.important = important

    def _serialize_to(self, write):
        write(serialize_identifier(self.name))
        write(':')
        _serialize_to(self.value, write)
        write(';')


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
    repr_format = ('<{self.__class__.__name__} '
                   '{self.prelude} {{ {self.content} }}>')

    def __init__(self, line, column, prelude, content):
        Node.__init__(self, line, column)
        self.prelude = prelude
        self.content = content

    def _serialize_to(self, write):
        _serialize_to(self.prelude, write)
        write('{')
        _serialize_to(self.content, write)
        write('}')


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
        see :func:`~webencodings.ascii_lower`.
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
    repr_format = ('<{self.__class__.__name__} '
                   '@{self.at_keyword} {self.prelude} {{ {self.content} }}>')

    def __init__(self, line, column,
                 at_keyword, lower_at_keyword, prelude, content):
        Node.__init__(self, line, column)
        self.at_keyword = at_keyword
        self.lower_at_keyword = lower_at_keyword
        self.prelude = prelude
        self.content = content

    def _serialize_to(self, write):
        write('@')
        write(serialize_identifier(self.at_keyword))
        _serialize_to(self.prelude, write)
        if self.content is None:
            write(';')
        else:
            write('{')
            _serialize_to(self.content, write)
            write('}')
