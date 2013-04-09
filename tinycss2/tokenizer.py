from __future__ import unicode_literals

import re
import sys

from .compat import unichr
from .utils import ascii_lower
# Some imports are at the bottom of this files.


_NUMBER_RE = re.compile(r'[-+]?([0-9]*\.)?[0-9]+')
_SCIENTIFIC_NOTATION_RE = re.compile('[eE][+-]?[0-9]+')
_HEX_ESCAPE_RE = re.compile(r'([0-9A-Fa-f]{1,6})[ \n\t]?')
_NON_WHITESPACE_CHAR_RE = re.compile(r'[^ \n\t]|$')
_NON_STRING_CHAR_RE = re.compile(r'''["'\\\n]|$''')
_NON_UNQUOTED_URL_CHAR_RE = re.compile(
    r'''[) \\\n"'(\x00-\t\x0E-\x1F\x7F-\x9F]|$''')

# All ASCII characters other than [a-zA-Z0-9_-]
_NON_NAME_CHAR_RE = re.compile('[%s]' % re.escape(''.join(
    c for c in map(chr, range(128)) if not re.match('[a-zA-Z0-9_-]', c))))


def tokenize(css):
    """The tokenizer.

    :param css: An Unicode string.
    :returns: A list of tokens.

    """
    css = (css.replace('\0', '\uFFFD')
           .replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n'))
    length = len(css)
    token_start_pos = pos = 0  # Character index in the css source.
    line = 1  # First line is line 1.
    last_newline = -1
    root = tokens = []
    end_char = None  # Pop the stack when encountering this character.
    stack = []  # Stack of nested blocks: (tokens, end_char) tuples.

    while pos < length:
        newline = css.rfind('\n', token_start_pos, pos)
        if newline != -1:
            line += 1 + css.count('\n', token_start_pos, newline)
            last_newline = newline
        # First character in a line is in column 1.
        column = pos - last_newline
        token_start_pos = pos
        c = css[pos]

        if c in ' \n\t':
            pos = _NON_WHITESPACE_CHAR_RE.search(css, pos + 1).start()
            tokens.append(WhitespaceToken(line, column))
            continue
        elif (c in 'Uu' and pos + 2 < length and css[pos + 1] == '+'
                and css[pos + 2] in '0123456789abcdefABCDEF?'):
            value, pos = _consume_unicode_range(css, pos + 2)
            tokens.append(UnicodeRangeToken(line, column, value))
            continue
        elif _is_ident_start(css, pos):
            value, pos = _consume_ident(css, pos)
            if not (pos < length and css[pos] == '('):  # Not a function
                tokens.append(IdentToken(line, column, value))
                continue
            pos += 1  # Skip the '('
            if ascii_lower(value) == 'url':
                value, pos = _consume_url(css, pos)
                tokens.append(
                    URLToken(line, column, value) if value is not None
                    else BadURLToken(line, column))
                continue
            arguments = []
            tokens.append(Function(pos, value, arguments))
            stack.append((tokens, end_char))
            end_char = ')'
            tokens = arguments
            continue

        match = _NUMBER_RE.match(css, pos)
        if match:
            is_integer = match.group(1) is None
            pos = match.end()
            if pos < length and css[pos] == '%':
                representation = css[token_start_pos:pos]
                value = (int if is_integer else float)(representation)
                tokens.append(DimensionToken(
                    line, column, value, representation, is_integer, '%'))
                pos += 1
                continue
            match = _SCIENTIFIC_NOTATION_RE.match(css, pos)
            if match:
                pos = match.end()
            elif _is_ident_start(css, pos):
                representation = css[token_start_pos:pos]
                value = (int if is_integer else float)(representation)
                unit, pos = _consume_ident(css, pos)
                tokens.append(DimensionToken(
                    line, column, value, representation, is_integer, unit))
                continue
            representation = css[token_start_pos:pos]
            value = (int if is_integer else float)(representation)
            tokens.append(NumberToken(
                line, column, value, representation, is_integer))
        elif c == '@':
            pos += 1
            if pos < length and _is_ident_start(css, pos):
                value, pos = _consume_ident(css, pos)
                tokens.append(AtKeywordToken(line, column, value))
            else:
                tokens.append(LiteralToken(line, column, '@'))
        elif c == '#':
            pos += 1
            if pos < length and (
                    css[pos] in '0123456789abcdefghijklmnopqrstuvwxyz'
                                '-_ABCDEFGHIJKLMNOPQRSTUVWXYZ'
                    # Valid escape:
                    or (css[pos] == '\\' and pos + 1 < length
                        and css[pos + 1] != '\n')):
                value, pos = _consume_ident(css, pos)
                tokens.append(HashToken(line, column, value))
            else:
                tokens.append(LiteralToken(line, column, '#'))
        elif c == '{':
            content = []
            tokens.append(CurlyBracketsBlock(pos, content))
            stack.append((tokens, end_char))
            end_char = '}'
            tokens = content
            pos += 1
        elif c == '[':
            content = []
            tokens.append(SquareBracketsBlock(pos, content))
            stack.append((tokens, end_char))
            end_char = ']'
            tokens = content
            pos += 1
        elif c == '(':
            content = []
            tokens.append(ParenthesesBlock(pos, content))
            stack.append((tokens, end_char))
            end_char = ')'
            tokens = content
            pos += 1
        elif c == end_char:  # Matching }, ] or )
            # The top-level end_char is None (never equal to a character),
            # so we never get here if the stack is empty.
            tokens, end_char = stack.pop()
            pos += 1
        elif c in '"\'':
            value, pos = _consume_quoted_string(css, pos)
            tokens.append(
                StringToken(line, column, value) if value is not None
                else BadStringToken(line, column))
        elif css.startswith('/*', pos):  # Comment
            pos = css.find('*/', pos + 2)
            if pos == -1:
                break
            pos += 2
        elif css.startswith('<!--', pos):
            tokens.append(LiteralToken(line, column, '<!--'))
            pos += 4
        elif css.startswith('-->', pos):
            tokens.append(LiteralToken(line, column, '-->'))
            pos += 3
        elif css.startswith('||', pos):
            tokens.append(LiteralToken(line, column, '||'))
            pos += 2
        elif c in '~|^$*':
            pos += 1
            if pos < length and css[pos] == '=':
                pos += 1
                tokens.append(LiteralToken(line, column, c + '='))
            else:
                tokens.append(LiteralToken(line, column, c))
        else:  # Colon, semicolon, comma or delim.
            tokens.append(LiteralToken(line, column, c))
            pos += 1
    return root


def _is_ident_start(css, pos):
    """Return True if the given position is the start of a CSS identifier."""
    c = css[pos]
    length = len(css)
#    if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
#        return True  # Fast path XXX
    if c == '-' and pos + 1 < length:
        pos += 1
        c = css[pos]
    return (
        c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
        or ord(c) > 0xFF  # Non-ASCII
        # Valid escape:
        or (c == '\\' and pos + 1 < length and css[pos + 1] != '\n'))


def _consume_ident(css, pos):
    """Return (unescaped_value, new_pos).

    Assumes pos starts at a valid identifier. See :func:`_is_ident_start`.

    """
    # http://dev.w3.org/csswg/css-syntax/#ident-state
    chunks = []
    length = len(css)
    while pos < length:
        start_pos = pos
        pos = _NON_NAME_CHAR_RE.search(css, pos).start()
        chuncks.append(css[start_pos:pos])
        if pos + 1 < length and css[pos] == '\\' and css[pos + 1] != '\n':
            # Valid escape
            c, pos = _consume_escape(css, pos + 1)
            chunks.append(c)
        else:
            break
    return ''.join(chunks), pos


def _consume_quoted_string(css, pos):
    """Return (unescaped_value, new_pos)."""
    # http://dev.w3.org/csswg/css-syntax/#double-quote-string-state
    # http://dev.w3.org/csswg/css-syntax/#single-quote-string-state
    quote = css[pos]
    assert quote in '"\''
    pos += 1
    chunks = []
    length = len(css)
    while pos < length:
        start_pos = pos
        pos = _NON_STRING_CHAR_RE.search(css, pos).start()
        chuncks.append(css[start_pos:pos])
        c = css[pos]
        if c == quote:
            pos += 1
            break
        elif c == '\\':
            pos += 1
            if pos < length:
                if css[pos] == '\n':  # Ignore escaped newlines
                    pos += 1
                else:
                    c, pos = _consume_escape(css, pos)
                    chunks.append(c)
            else:  # "Escaped" EOF
                return None, pos  # bad-string
        elif c == '\n':  # Unescaped newline
            return None, pos  # bad-string
        else:  # The other quote
            pos += 1
            chunks.append(c)
    return ''.join(chunks), pos


def _consume_escape(css, pos):
    r"""Return (unescaped_char, new_pos).

    Assumes a valid escape:
    pos is just after '\', there’s at least one more char, and it’s not '\n'.

    """
    # http://dev.w3.org/csswg/css-syntax/#consume-an-escaped-character
    hex_match = _HEX_ESCAPE_RE.match(css, pos)
    if hex_match:
        codepoint = int(hex_match.group(1), 16)
        return (unichr(codepoint) if codepoint <= sys.maxunicode else '\uFFFE',
                match.end())
    return css[pos], pos + 1


def _consume_url(css, pos):
    """Return (unescaped_url, new_pos)

    The given pos is assume to be just after the '(' of 'url('.

    """
    length = len(css)
    # http://dev.w3.org/csswg/css-syntax/#url-state
    # Skip whitespace
    pos = _NON_WHITESPACE_CHAR_RE.search(css, pos).start()
    if pos >= length:  # EOF
        return None, pos  # bad-url
    c = css[pos]
    if c in '"\'':
        # http://dev.w3.org/csswg/css-syntax/#url-double-quote-state0
        # http://dev.w3.org/csswg/css-syntax/#url-single-quote-state0
        value, pos = _consume_quoted_string()
    elif c == ')':
        return '', pos + 1
    else:
        # http://dev.w3.org/csswg/css-syntax/#url-unquoted-state0
        chunks = []
        while 1:
            start_pos = pos
            pos = _NON_UNQUOTED_URL_CHAR_RE.search(css, pos).start()
            chuncks.append(css[start_pos:pos])
            if pos >= length:  # EOF
                return ''.join(chunks), pos
            c = css[pos]
            pos += 1
            if c == ')':
                return ''.join(chunks), pos
            elif c in ' \n':
                value = ''.join(chunks)
                break
            elif c == '\\' and pos < length and css[pos] != '\n':
                # Valid escape
                c, pos = _consume_escape(css, pos)
                chunks.append(c)
            else:
                value = None
                break

    if value is not None:
        # http://dev.w3.org/csswg/css-syntax/#url-end-state0
        pos = _NON_WHITESPACE_CHAR_RE.search(css, pos).start()
        if pos >= length or css[pos] == ')':
            return value, pos
    # http://dev.w3.org/csswg/css-syntax/#bad-url-state0
    return None, (css.find(')', pos) + 1) or length  # bad-url


def _consume_unicode_range(css, pos):
    """Return (range, new_pos)

    The given pos is assume to be just after the '+' of 'U+' or 'u+'.

    """
    # http://dev.w3.org/csswg/css-syntax/#unicode-range-state0
    length = len(css)
    start_pos = pos
    max_pos = min(pos + 6, length)
    while pos < max_pos and css[pos] in '0123456789abcdefABCDEF':
        pos += 1
    hex_1 = css[start_pos:pos]

    start_pos = pos
    max_pos = min(pos + 6 - len(hex_1), length)
    while pos < max_pos and css[pos] == '?':
        pos += 1
    question_marks = pos - start_pos

    if question_marks:
        hex_2 = hex_1 + 'F' * question_marks
        hex_1 += '0' * question_marks
    elif (pos + 1 < length and css[pos] == '-'
            and css[pos + 1] in '0123456789abcdefABCDEF'):
        start_pos = pos
        max_pos = min(pos + 6, length)
        while pos < max_pos and css[pos] in '0123456789abcdefABCDEF':
            pos += 1
        hex_2 = css[start_pos:pos]
    else:
        hex_2 = hex_1
    start = int(hex_1, 16)
    end = int(hex_2, 16)

    # http://dev.w3.org/csswg/css-syntax/#set-the-unicode-range-tokens-range0
    if start > sys.maxunicode or end < start:
        return None, pos
    else:
        return (unichr(start), unichr(min(end, sys.maxunicode))), pos


# Moved here so that pyflakes can detect naming typos above.
from .tokens import *
