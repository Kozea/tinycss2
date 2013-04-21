VERSION = '0.1'


def ascii_lower(string):
    r"""Transform (only) ASCII letters to lower case: A-Z is mapped to a-z.

    :param string: An Unicode string.
    :returns: A new Unicode string.

    This should be used for CSS-defined keywords,
    as they are `case-insensitive within the ASCII range
    <http://www.w3.org/TR/CSS21/syndata.html#characters>`_.

    This is different from just using :meth:`unicode.lower`
    which will also affect non-ASCII characters,
    sometimes mapping them into the ASCII range:

        >>> keyword = u'bac\N{KELVIN SIGN}ground'
        >>> assert keyword.lower() == 'background'
        >>> assert ascii_lower(keyword) != 'background'

    """
    return string.encode('utf8').lower().decode('utf8')


def strip_whitespace_tokens(token_list):
    """Remove leading and trailing whitespace tokens.

    :param token_list: A list of tokens.
    :returns: A new list of tokens.

    """
    for i, token in enumerate(token_list):
        if token.type != 'whitespace':
            token_list = token_list[i:]
            while token_list[-1].type == 'whitespace':
                token_list.pop()
            return token_list
    return []


def split_on_comma_tokens(token_list):
    """Split on comma token, and strip whitespace on each part.

    :param token_list: A list of tokens.
    :returns: A new list of lists of tokens.

    """
    result = []
    item = []
    for token in token_list:
        if token == ',':
            result.append(strip_whitespace_tokens(item))
            item = []
        else:
            item.append(token)
    result.append(strip_whitespace_tokens(item))
    return result
