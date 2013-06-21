import webencodings


VERSION = '0.1'


def decode_css_bytes(css_bytes, protocol_encoding=None, link_encoding=None,
                     document_encoding=None):
    """Determine the character encoding and decode a CSS stylesheet.

    :param css_bytes: The stylesheet as a byte string.
    :param protocol_encoding:
        The encoding label, if any, defined by HTTP or equivalent protocol.
        (e.g. via the ``charset`` parameter of the ``Content-Type`` header.)
    :param link_encoding:
        The encoding label, if any, defined by the stylesheet linking mechanism
        (e.g. ``charset`` attribute on the ``<link>`` element or
        ``<?xml-stylesheet?>`` processing instruction
        that caused the style sheet to be included.)
    :param document_encoding:
        The encoding label, if any, of the referring stylesheet or document.
    :returns:
        An Unicode string.
        The ``@charset`` rule is still part of the string,
        but any Byte Order Mark is not.

    """
    # http://dev.w3.org/csswg/css-syntax/#the-input-byte-stream
    fallback = webencodings.lookup(protocol_encoding)
    if fallback:
        return webencodings.decode(css_bytes, fallback)
    if css_bytes.startswith(b'@charset "'):
        # 10 is len(b'@charset "')
        # 100 is abitrary so that no encoding label is more than 100-10 bytes.
        end_quote = css_bytes.find('"', 10, 100)
        if end_quote != -1 and css_bytes.startswith('";', end_quote):
            fallback = webencodings.lookup(css_bytes[10:end_quote])
            if fallback:
                if fallback.name in ('utf-16be', 'utf-16le'):
                    return webencodings.decode(css_bytes, webencodings.UTF8)
                return webencodings.decode(css_bytes, fallback)
    fallback = webencodings.lookup(link_encoding)
    if fallback:
        return webencodings.decode(css_bytes, fallback)
    fallback = webencodings.lookup(document_encoding)
    if fallback:
        return webencodings.decode(css_bytes, fallback)
    return webencodings.decode(css_bytes, webencodings.UTF8)


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

        >>> keyword = u'Bac\N{KELVIN SIGN}ground'
        >>> assert keyword.lower() == u'background'
        >>> assert ascii_lower(keyword) != keyword.lower()
        >>> assert ascii_lower(keyword) == u'bac\N{KELVIN SIGN}ground'

    """
    # This turns out to be faster than unicode.translate()
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
