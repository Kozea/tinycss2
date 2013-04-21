from .nodes import ParseError, Declaration, AtRule, QualifiedRule


def parse_one_declaration(tokens):
    """
    :param tokens: An iterable of tokens.
    :returns:
        A :class:`~tinycss2.nodes.Declaration`
        or :class:`~tinycss2.nodes.ParseError`.

    """
    tokens = iter(tokens)
    for token in tokens:
        if token.type == 'ident':
            name = token
            break
        elif token.type != 'whitespace':
            return ParseError(
                token.line, token.column,
                'Expected ident for declaration name, got %s.' % token.type)
    else:
        return ParseError(
            None, None, 'Expected ident for declaration name, found EOF')

    for token in tokens:
        if token == ':':
            break
        elif token.type != 'whitespace':
            return ParseError(
                token.line, token.column,
                "Expected ':' after declaration name, got %s." % token.type)
    else:
        return ParseError(
            None, None, "Expected ':' after declaration name, found EOF")

    value = list(tokens)

    important = False
    reversed_value = iter(enumerate(reversed(value), 1))
    for i, token in reversed_value:
        if token.type == 'ident' and token.value == 'important':
            for i, token in reversed_value:
                if token == '!':
                    important = True
                    value = value[:-i]
                elif token.type != 'whitespace':
                    break
        elif token.type != 'whitespace':
            break

    return Declaration(name.line, name.column,
                       name.value, name.case_sensitive_value, value, important)


def parse_declarations(tokens, with_at_rules=False):
    """

    :param tokens: An iterable of tokens.
    :param with_at_rules: Whether to allow at-rules mixed with declarations.
    :returns:
        A generator that yields either
        :class:`~tinycss2.nodes.Declaration`,
        :class:`~tinycss2.nodes.ParseError`,
        or (if :obj:`with_at_rules` is true) :class:`~tinycss2.nodes.AtRule`.

    """
    tokens = iter(tokens)
    for token in tokens:
        if token.type == 'whitespace':
            continue
        elif with_at_rules and token.type == 'at-keyword':
            yield _parse_at_rule_internal(token, tokens)
            continue
        declaration_tokens = [token]
        for token in tokens:
            if token == ';':
                yield parse_one_declaration(declaration_tokens)
                break
            else:
                declaration_tokens.append(token)
        else:
            yield parse_one_declaration(declaration_tokens)


def parse_one_rule(tokens, is_top_level=True):
    """

    :param tokens: An iterable of tokens.
    :param is_top_level: False is :obj:`tokens` is eg. the body of an at-rule.
    :returns:
        A :class:`~tinycss2.nodes.QualifiedRule`,
        :class:`~tinycss2.nodes.AtRule`,
        or :class:`~tinycss2.nodes.ParseError`.

    """
    rules = parse_rules(tokens, is_top_level)
    first = next(rules, None)
    if first is None:
        return ParseError(None, None, 'Expected a rule, got EOF')
    elif first.type == 'error':
        return first
    second = next(rules, None)
    if second is not None:
        return ParseError(None, None, 'Expected a single rule, '
                          'got %s after the first rule.' % second.type)
    return first


def parse_rules(tokens, is_top_level=True):
    """

    :param tokens: An iterable of tokens.
    :param is_top_level: False is :obj:`tokens` is eg. the body of an at-rule.
    :returns:
        A generator that yields either
        :class:`~tinycss2.nodes.QualifiedRule`,
        :class:`~tinycss2.nodes.AtRule`,
        or :class:`~tinycss2.nodes.ParseError`.

    """
    tokens = iter(tokens)
    for token in tokens:
        if token.type == 'whitespace' or (
                is_top_level and token in ('<!--', '-->')):
            continue
        elif token.type == 'at-keyword':
            yield _parse_at_rule_internal(token, tokens)
            continue
        first_head_token = token
        head = [token]
        for token in tokens:
            if token.type == '{} block':
                yield QualifiedRule(first_head_token.line,
                                    first_head_token.column, head, token)
                break
            else:
                head.append(token)
        else:
            yield ParseError(
                None, None, 'Expected qualified rule body, got EOF.')


def _parse_at_rule_internal(at_keyword, tokens):
    """
    :param at_keyword: A token of at-keyword type.
    :param tokens: An **iterator** of tokens, only consumed for this at-rule.
    :returns:
        A :class:`~tinycss2.nodes.AtRule`,
        or :class:`~tinycss2.nodes.ParseError`.

    """
    head = []
    for token in tokens:
        if token.type == '{} block':
            body = token
            break
        elif token == ';':
            body = None
            break
        else:
            head.append(token)
    else:
        body = None
    return AtRule(
        at_keyword.line, at_keyword.column,
        at_keyword.value, at_keyword.case_sensitive_value, head, body)
