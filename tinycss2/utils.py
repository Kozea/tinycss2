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
