# coding: utf-8

from .tokenizer import parse_component_value_list
from .ast import ParseError, Declaration, AtRule, QualifiedRule
from ._compat import basestring


def _to_token_iterator(input):
    """

    :param input: A string or an iterable of :term:`component values`.
    :returns: A iterator yielding :term:`component values`.

    """
    # Accept ASCII-only byte strings on Python 2, with implicit conversion.
    if isinstance(input, basestring):
        input = parse_component_value_list(input)
    return iter(input)


def _next_non_whitespace(tokens):
    """Return the next non-<whitespace> token.

    :param tokens: An *iterator* yielding :term:`component values`.
    :returns: A :term:`component value`, or :obj:`None`.

    """
    for token in tokens:
        if token.type != 'whitespace':
            return token


def parse_one_component_value(input):
    """Parse a single :diagram:`component value`.

    This is used e.g. for an attribute value
    referred to by ``attr(foo length)``.

    :param input:
        A :term:`string`, or an iterable of :term:`component values`.
    :returns:
        A :term:`component value`, or a :class:`~tinycss2.ast.ParseError`.

    """
    tokens = _to_token_iterator(input)
    first = _next_non_whitespace(tokens)
    second = _next_non_whitespace(tokens)
    if first is None:
        return ParseError(1, 1, 'empty', 'Input is empty')
    if second is not None:
        return ParseError(
            second.source_line, second.source_column, 'extra-input',
            'Got more than one token')
    else:
        return first


def parse_one_declaration(input):
    """Parse a single :diagram:`declaration`.

    This is used e.g. for a declaration in an `@supports
    <http://dev.w3.org/csswg/css-conditional/#at-supports>`_ test.

    :param input:
        A :term:`string`, or an iterable of :term:`component values`.
    :returns:
        A :class:`~tinycss2.ast.Declaration`
        or :class:`~tinycss2.ast.ParseError`.

    """
    tokens = _to_token_iterator(input)
    first_token = _next_non_whitespace(tokens)
    if first_token is None:
        return ParseError(1, 1, 'empty', 'Input is empty')
    return _parse_declaration(first_token, tokens)


def _parse_declaration(first_token, tokens):
    """Parse a declaration.

    Consume :obj:`tokens` until the end of the declaration or the first error.

    :param first_token: The first :term:`component value` of the rule.
    :param tokens: An *iterator* yielding :term:`component values`.
    :returns:
        A :class:`~tinycss2.ast.Declaration`
        or :class:`~tinycss2.ast.ParseError`.

    """
    name = first_token
    if name.type != 'ident':
        return ParseError(name.source_line, name.source_column, 'invalid',
                          'Expected <ident> for declaration name, got %s.'
                          % name.type)

    colon = _next_non_whitespace(tokens)
    if colon is None:
        return ParseError(name.source_line, name.source_column, 'invalid',
                          "Expected ':' after declaration name, got EOF")
    elif colon != ':':
        return ParseError(colon.source_line, colon.source_column, 'invalid',
                          "Expected ':' after declaration name, got %s."
                          % colon.type)

    value = []
    state = 'value'
    for i, token in enumerate(tokens):
        if state == 'value' and token == '!':
            state = 'bang'
            bang_position = i
        elif state == 'bang' and token.type == 'ident' \
                and token.lower_value == 'important':
            state = 'important'
        elif token.type != 'whitespace':
            state = 'value'
        value.append(token)

    if state == 'important':
        del value[bang_position:]

    return Declaration(name.source_line, name.source_column, name.value,
                       name.lower_value, value, state == 'important')


def _consume_declaration_in_list(first_token, tokens):
    """
    Same as :func:`_consume_declaration`, but consume to the end
    of the (possibly invalid) declaration.

    """
    other_declaration_tokens = []
    for token in tokens:
        if token == ';':
            break
        other_declaration_tokens.append(token)
    return _parse_declaration(first_token, iter(other_declaration_tokens))


def parse_declaration_list(input):
    """Parse a :diagram:`declaration list` (which may also contain at-rules).

    This is used e.g. for the :attr:`~tinycss2.ast.QualifiedRule.content`
    of a style rule or ``@page`` rule,
    or for the `style` attribute of an HTML element.

    In contexts that don’t expect any at-rule,
    all :class:`~tinycss2.ast.AtRule` objects
    should simply be rejected as invalid.

    :param input: A string or an iterable of :term:`component values`.
    :returns:
        A list of
        :class:`~tinycss2.ast.Declaration`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects

    """
    tokens = _to_token_iterator(input)
    return [
        _consume_at_rule(token, tokens) if token.type == 'at-keyword'
        else _consume_declaration_in_list(token, tokens)
        for token in tokens if token.type != 'whitespace' and token != ';']


def parse_one_rule(input):
    """Parse a single :diagram:`qualified rule` or :diagram:`at-rule`.

    This would be used e.g. by `insertRule()
    <http://dev.w3.org/csswg/cssom/#dom-cssstylesheet-insertrule>`_
    in an implementation of CSSOM.

    :param input: A string or an iterable of :term:`component values`.
    :returns:
        A :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        or :class:`~tinycss2.ast.ParseError` objects.

    """
    tokens = _to_token_iterator(input)
    first = _next_non_whitespace(tokens)
    if first is None:
        return ParseError(1, 1, 'empty', 'Input is empty')

    rule = _consume_rule(first, tokens)
    next = _next_non_whitespace(tokens)
    if next is not None:
        return ParseError(
            next.source_line, next.source_column, 'extra-input',
            'Expected a single rule, got %s after the first rule.' % next.type)
    return rule


def parse_rule_list(input):
    """Parse a non-top-level :diagram:`rule list`.

    This is used for parsing the :attr:`~tinycss2.ast.AtRule.content`
    of nested rules like ``@media``.
    This differs from :func:`parse_stylesheet` in that
    top-level ``<!--`` and ``-->`` tokens are not ignored.

    :param input: A string or an iterable of :term:`component values`.
    :returns:
        A list of
        :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects.

    """
    tokens = _to_token_iterator(input)
    return [_consume_rule(token, tokens) for token in tokens
            if token.type != 'whitespace']


def parse_stylesheet(input):
    """Parse :diagram:`stylesheet` from text.

    This is used e.g. for a ``<style>`` HTML element.

    This differs from :func:`parse_rule_list` in that
    top-level ``<!--`` and ``-->`` tokens are ignored.

    :param input: A string or an iterable of :term:`component values`.
    :returns:
        A list of
        :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects.

    """
    tokens = _to_token_iterator(input)
    return [_consume_rule(token, tokens) for token in tokens
            if token.type != 'whitespace' and token not in ('<!--', '-->')]


def _consume_rule(first_token, tokens):
    """Parse a qualified rule or at-rule.

    Consume just enough of :obj:`tokens` for this rule.

    :param first_token: The first :term:`component value` of the rule.
    :param tokens: An *iterator* yielding :term:`component values`.
    :returns:
        A :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        or :class:`~tinycss2.ast.ParseError`.

    """
    if first_token.type == 'at-keyword':
        return _consume_at_rule(first_token, tokens)
    if first_token.type == '{} block':
        prelude = []
        block = first_token
    else:
        prelude = [first_token]
        for token in tokens:
            if token.type == '{} block':
                block = token
                break
            prelude.append(token)
        else:
            return ParseError(
                prelude[-1].source_line, prelude[-1].source_column, 'invalid',
                'EOF reached before {} block for a qualified rule.')
    return QualifiedRule(first_token.source_line, first_token.source_column,
                         prelude, block.content)


def _consume_at_rule(at_keyword, tokens):
    """Parse an at-rule.

    Consume just enough of :obj:`tokens` for this rule.

    :param at_keyword: The :class:`AtKeywordToken` object starting this rule.
    :param tokens: An *iterator* yielding :term:`component values`.
    :returns:
        A :class:`~tinycss2.ast.QualifiedRule`,
        or :class:`~tinycss2.ast.ParseError`.

    """
    prelude = []
    content = None
    for token in tokens:
        if token.type == '{} block':
            content = token.content
            break
        elif token == ';':
            break
        prelude.append(token)
    return AtRule(at_keyword.source_line, at_keyword.source_column,
                  at_keyword.value, at_keyword.lower_value, prelude, content)
