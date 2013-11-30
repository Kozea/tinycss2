from webencodings import lookup, decode, UTF8

from .tokenizer import parse_component_value_list
from .parser import parse_stylesheet


def decode_stylesheet_bytes(css_bytes, protocol_encoding=None,
                            link_encoding=None, document_encoding=None):
    """Determine the character encoding of a CSS stylesheet and decode it.

    This is based on the presence of a BOM, an ``@charset`` rule,
    and encoding meta-information.

    The parameters are the same as :func:`parse_stylesheet_bytes`.

    :returns: an Unicode string.

    """
    # http://dev.w3.org/csswg/css-syntax/#the-input-byte-stream
    fallback = lookup(protocol_encoding)
    if fallback:
        return decode(css_bytes, fallback)
    if css_bytes.startswith(b'@charset "'):
        # 10 is len(b'@charset "')
        # 100 is abitrary so that no encoding label is more than 100-10 bytes.
        end_quote = css_bytes.find('"', 10, 100)
        if end_quote != -1 and css_bytes.startswith('";', end_quote):
            fallback = lookup(css_bytes[10:end_quote])
            if fallback:
                if fallback.name in ('utf-16be', 'utf-16le'):
                    return decode(css_bytes, UTF8)
                return decode(css_bytes, fallback)
    fallback = lookup(link_encoding)
    if fallback:
        return decode(css_bytes, fallback)
    fallback = lookup(document_encoding)
    if fallback:
        return decode(css_bytes, fallback)
    return decode(css_bytes, UTF8)


def parse_stylesheet_bytes(css_bytes, protocol_encoding=None,
                           link_encoding=None, document_encoding=None):
    """Parse stylesheet from bytes.

    :param css_bytes: A byte string.
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
        A list of
        :class:`~tinycss2.ast.QualifiedRule`,
        :class:`~tinycss2.ast.AtRule`,
        and :class:`~tinycss2.ast.ParseError` objects.

    """
    return parse_stylesheet(parse_component_value_list(decode_stylesheet_bytes(
        css_bytes, protocol_encoding, link_encoding, document_encoding)))
