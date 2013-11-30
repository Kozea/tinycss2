from webencodings import lookup, decode, UTF8

from .tokenizer import parse_component_value_list
from .parser import parse_stylesheet


def decode_stylesheet_bytes(css_bytes, protocol_encoding=None,
                            environment_encoding=None):
    """Determine the character encoding of a CSS stylesheet and decode it.

    This is based on the presence of a :abbr:`BOM (Byte Order Mark)`,
    an ``@charset`` rule,
    and encoding meta-information.

    :param css_bytes: A byte string.
    :param protocol_encoding:
        The encoding label, if any, defined by HTTP or equivalent protocol.
        (e.g. via the ``charset`` parameter of the ``Content-Type`` header.)
    :param environment_encoding:
        A :class:`webencodings.Encoding` object
        for the `environment encoding
        <http://www.w3.org/TR/css-syntax/#environment-encoding>`_,
        if any.
    :returns:
        A 2-tuple of a decoded Unicode string
        and the :class:`webencodings.Encoding` object that was used.

    """
    # http://dev.w3.org/csswg/css-syntax/#the-input-byte-stream
    if protocol_encoding:
        fallback = lookup(protocol_encoding)
        if fallback:
            return decode(css_bytes, fallback)
    if css_bytes.startswith(b'@charset "'):
        # 10 is len(b'@charset "')
        # 100 is arbitrary so that no encoding label is more than 100-10 bytes.
        end_quote = css_bytes.find(b'"', 10, 100)
        if end_quote != -1 and css_bytes.startswith(b'";', end_quote):
            fallback = lookup(css_bytes[10:end_quote].decode('latin1'))
            if fallback:
                if fallback.name in ('utf-16be', 'utf-16le'):
                    return decode(css_bytes, UTF8)
                return decode(css_bytes, fallback)
    if environment_encoding:
        return decode(css_bytes, environment_encoding)
    return decode(css_bytes, UTF8)


def parse_stylesheet_bytes(css_bytes, protocol_encoding=None,
                           environment_encoding=None):
    """Parse stylesheet from bytes.

    :param css_bytes: A byte string.
    :param protocol_encoding:
        The encoding label, if any, defined by HTTP or equivalent protocol.
        (e.g. via the ``charset`` parameter of the ``Content-Type`` header.)
    :param environment_encoding:
        A :class:`webencodings.Encoding` object
        for the `environment encoding
        <http://www.w3.org/TR/css-syntax/#environment-encoding>`_,
        if any.
    :returns:
        A 2-tuple of a list
        and the :class:`webencodings.Encoding` object that was used.
        The list contains
        :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects.

    """
    css_unicode, encoding = decode_stylesheet_bytes(
        css_bytes, protocol_encoding, environment_encoding)
    return parse_stylesheet(parse_component_value_list(css_unicode)), encoding
