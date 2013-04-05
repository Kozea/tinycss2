from __future__ import unicode_literals

import re
import sys

from .compat import unichr
from .utils import ascii_lower
# Some imports are at the bottom of this files.


_HEX_ESCAPE_RE = re.compile(r'([0-9A-Fa-f]{1,6})[ \n\t]?')
_NON_WHITESPACE_CHAR_RE = re.compile(r'[^ \n\t]|$')
_NON_STRING_CHAR_RE = re.compile(r'''["'\\\n]|$''')

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
    pos = 0  # Character index in the css source.
    line = 1  # First line is line 1.
    last_newline = -1
    root = tokens = []
    end_char = None  # Pop the stack when encountering this character.
    stack = []  # Stack of nested blocks: (tokens, end_char) tuples.

    while pos < length:
        # First character in a line is in column 1.
        column = pos - last_newline
        token_start_pos = pos
        c = css[pos]
        if c in ' \n\t':
            pos = _NON_WHITESPACE_CHAR_RE.search(css, pos + 1).start()
            tokens.append(WhitespaceToken(line, column))
        elif _is_ident_start(css, pos):
            # TODO: unicode-range
            #if (c in 'Uu' and pos + 2 < length and css[pos + 1] == '+'
            #    and css[pos + 2] in '0123456789abcdefABCDEF')
            value, pos = _consume_ident(css, pos)
            if pos < length and css[pos] == '(':
                # TODO: if ascii_lower(value) == 'url':
                arguments = []
                tokens.append(Function(pos, value, arguments))
                stack.append((tokens, end_char))
                end_char = ')'
                tokens = arguments
                pos += 1
            else:
                tokens.append(IdentToken(line, column, value))
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
                    or (css[pos] == '\\' and pos + 1 < length
                        and css[pos + 1] != '\n')):
                value, pos = _consume_ident(css, pos)
                tokens.append(HashToken(line, column, value))
            else:
                tokens.append(LiteralToken(line, column, '#'))
        # TODO: number, dimension, percentage
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

        newline = css.rfind('\n', token_start_pos, pos)
        if newline != -1:
            line += 1 + css.count('\n', token_start_pos, newline)
            last_newline = newline
    return root


def _is_ident_start(css, pos):
    """Return True if the given position is the start of a CSS identifier."""
    c = css[pos]
#    if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
#        return True  # Fast path XXX
    if c == '-' and pos + 1 >= length:
        pos += 1
        c = css[pos]
    return (
        c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
        or ord(c) > 0xFF
        or (c == '\\' and pos + 1 < length and css[pos + 1] != '\n'))


def _consume_ident(css, pos):
    """Return (unescaped_value, new_pos)."""
    chunks = []
    length = len(css)
    while pos < length:
        new_pos = _NON_NAME_CHAR_RE.search(css, pos).start()
        chuncks.append(css[pos:new_pos])
        pos = new_pos
        if pos + 1 < length and css[pos] == '\\' and css[pos + 1] != '\n':
            c, pos = _consume_escape(css, pos + 1)
            chunks.append(c)
        else:
            break
    return ''.join(chunks), pos


def _consume_quoted_string(css, pos):
    """Return (unescaped_value, new_pos)."""
    quote = css[pos]
    assert quote in '"\''
    pos += 1
    chunks = []
    length = len(css)
    while pos < length:
        new_pos = _NON_STRING_CHAR_RE.search(css, pos).start()
        chuncks.append(css[pos:new_pos])
        pos = new_pos
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
    hex_match = _HEX_ESCAPE_RE.match(css, pos)
    if hex_match:
        codepoint = int(hex_match.group(1), 16)
        return (unichr(codepoint) if codepoint <= sys.maxunicode else '\uFFFE',
                match.end())
    return css[pos], pos + 1


# Moved here so that pyflakes can detect naming typos above.
from .tokens import *
