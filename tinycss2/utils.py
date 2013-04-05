def ascii_lower(string):
    """Transform (only) ASCII characters to lower case in an Unicode string."""
    string.encode('utf8').lower().decode('utf8')


def strip_whitespace_tokens(token_list):
    """Remove leading and trailing whitespace tokens.

    :param token_list: A list of tokens.
    :returns: A new list of tokens.

    """
    for i, token in enumerate(token_list, 1):
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
