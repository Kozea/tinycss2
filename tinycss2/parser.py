from .tokenizer import parse_component_value_list
from .ast import ParseError, Declaration, AtRule, QualifiedRule
from ._compat import basestring


def _to_token_iterator(input):
    """

    :param input: A string or an iterable yielding :ref:`component values`.
    :returns: A iterator yielding :ref:`component values`.

    """
    # Accept ASCII-only byte strings on Python 2, with implicit conversion.
    if isinstance(input, basestring):
        input = parse_component_value_list(input)
    return iter(input)


def _next_non_whitespace(tokens):
    """Return the next non-<whitespace> token.

    :param tokens: An *iterator* yielding :ref:`component values`.
    :returns: A :ref:`component value`, or :obj:`None`.

    """
    for token in tokens:
        if token.type != 'whitespace':
            return token


def parse_one_component_value(input):
    """Parse a single component value.

    :param input:
        A :ref:`string`, or an iterable yielding :ref:`component values`.
    :returns: A :ref:`component value`, or a :class:`~tinycss2.ast.ParseError`.

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
    """Parse a single declaration.

    :param input:
        A :ref:`string`, or an iterable yielding :ref:`component values`.
    :returns:
        A :class:`~tinycss2.ast.Declaration`
        or :class:`~tinycss2.ast.ParseError`.

    """
    tokens = _to_token_iterator(input)
    first_token = _next_non_whitespace(tokens)
    if first_token is None:
        return ParseError(1, 1, 'empty', 'Input is empty')
    result = _consume_declaration(first_token, tokens)
    if result.type != 'error':
        next = _next_non_whitespace(tokens)
        if next is not None:
            return ParseError(
                next.source_line, next.source_column, 'extra-input',
                'Expected a single rule, got %s after the first rule.'
                % next.type)
    return result


def _consume_declaration(first_token, tokens):
    """Parse a declaration.

    Consume :obj:`tokens` until the end of the declaration or the first error.

    :param tokens: An *iterator* yielding :ref:`component values`.
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
    important = False
    for token in tokens:
        if token == ';':
            break
        elif token == '!':
            token = _next_non_whitespace(tokens)
            if (token is not None and token.type == 'ident'
                    and token.lower_value == 'important'):
                token = _next_non_whitespace(tokens)
                if token is None or token == ';':
                    important = True
                    break
            return ParseError(
                token.source_line, token.source_column, 'invalid',
                "Invalid '!' value, expected 'important'.")
        else:
            value.append(token)

    return Declaration(name.source_line, name.source_column, name.value,
                       name.lower_value, value, important)


def _consume_whole_declaration(first_token, tokens):
    """
    Same as :func:`_consume_declaration`, but consume to the end
    of the (possibly invalid) declaration.

    """
    result = _consume_declaration(first_token, tokens)
    if result.type == 'error':
        # Consume until the next ';' or EOF.
        for token in tokens:
            if token == ';':
                break
    return result


def parse_declaration_list(input):
    """Parse a mixed list of declarations and at-rules.

    :param input: A string or an iterable yielding :ref:`component values`.
    :returns:
        A list of
        :class:`~tinycss2.ast.Declaration`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects

    """
    tokens = _to_token_iterator(input)
    return [
        _consume_at_rule(token, tokens) if token.type == 'at-keyword'
        else _consume_whole_declaration(token, tokens)
        for token in tokens if token.type != 'whitespace' and token != ';']


def parse_one_rule(input):
    """Parse a single qualified rule or at-rule.

    :param input: A string or an iterable yielding :ref:`component values`.
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
    """Parse a mixed list of qualified rules and at-rules.

    This is meant for parsing eg. the content of an ``@media`` rule.
    This differs from :func:`parse_stylesheet` in that
    top-level ``<!--`` and ``-->`` tokens are not ignored.

    :param input: A string or an iterable yielding :ref:`component values`.
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
    """Parse stylesheet: a mixed list of qualified rules and at-rules.

    This differs from :func:`parse_rule_list` in that
    top-level ``<!--`` and ``-->`` tokens are ignored.

    :param input: A string or an iterable yielding :ref:`component values`.
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

    :param first_token: The first :ref:`component value` of the rule.
    :param tokens: An *iterator* yielding :ref:`component values`.
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
    :param tokens: An *iterator* yielding :ref:`component values`.
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
