from __future__ import unicode_literals
import re

from .compat import unichr
# Some imports are at the bottom of this files.


_HEX_ESCAPE_RE = re.compile(r'([0-9A-Fa-f]{1,6})[ \n\t]?')
_NON_STRING_CHAR_RE = re.compile(r'''["'\\\n]''')
_NON_NAME_CHAR_RE = re.compile('[%s]' % re.escape(''.join(
    c for c in map(chr, range(128)) if not re.match('[a-zA-Z0-9_-]', c))))


def tokenize(input):
    """The tokenizer.

    :param input: An Unicode string, with any Byte Order Mark removed.
    :returns: A list of tokens.

    """
    input = (input.replace('\0', '\uFFFD')
             .replace('\r\n', '\n').replace('\r', '\n').replace('\f', '\n'))
    length = len(input)
    pos = 0
    root = tokens = []
    stack = []
    end_char = None

    def is_ident_start(pos):
        c = input[pos]
#        if c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_':
#            return True  # Fast path XXX
        if c == '-' and pos + 1 >= length:
            pos += 1
            c = input[pos]
        return (
            c in 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_'
            or ord(c) > 0xFF
            or (c == '\\' and pos + 1 < length and input[pos + 1] != '\n'))

    while pos < length:
        c = input[pos]
        if c in ' \n\t':
            pos += 1
            while pos < length and input[pos] in ' \n\t':
                pos += 1
            tokens.append(WHITESPACE_TOKEN)
        elif is_ident_start(pos):
            result, pos = _consume_ident(input, pos)
            tokens.append(IdentToken(result))
        elif c == '{':
            content = []
            tokens.append(CurlyBracketsBlock(content))
            stack.append((tokens, end_char))
            end_char = '}'
            tokens = content
            pos += 1
        elif c == '[':
            content = []
            tokens.append(SquareBracketsBlock(content))
            stack.append((tokens, end_char))
            end_char = ']'
            tokens = content
            pos += 1
        elif c == '(':
            content = []
            tokens.append(ParenthesesBlock(content))
            stack.append((tokens, end_char))
            end_char = ')'
            tokens = content
            pos += 1
        elif c == end_char:  # Matching }, ] or )
            tokens, end_char = stack.pop()
            pos += 1
        elif c in '"\'':
            result, pos = _consume_quoted_string(input, pos)
            tokens.append(StringToken(result) if result is not None
                          else BAD_STRING_TOKEN)
        elif input.startswith('/*', pos):  # Comment
            pos = input.find('*/', pos + 2)
            if pos == -1:
                break
            pos += 2
        elif input.startswith('<!--', pos):
            tokens.append(CDO_TOKEN)
            pos += 4
        elif input.startswith('-->', pos):
            tokens.append(CDC_TOKEN)
            pos += 3
        elif c in '~|^$*':
            pos += 1
            if pos < length and input[pos] == '=':
                pos += 1
                tokens.append(ATTRIBUTE_OPERATOR_TOKENS[c])
            else:
                tokens.append(LITERAL_TOKENS[c])
        else:  # Colon, semicolon, comma or delim.
            tokens.append(LITERAL_TOKENS[c])
            pos += 1
    return root


def _consume_ident(input, pos):
    chunks = []
    length = len(input)
    while pos < length:
        match = _NON_NAME_CHAR_RE.match(input, pos)
        if not match:
            chuncks.append(input[pos:])
            pos = length
            break
        new_pos = match.start()
        chuncks.append(input[pos:new_pos])
        pos = new_pos
        if pos + 1 < length and input[pos] == '\\' and input[pos + 1] != '\n':
            c, pos = _consume_escape(input, pos + 1)
            chunks.append(c)
        else:
            break
    return ''.join(chunks), pos


def _consume_quoted_string(input, pos):
    quote = input[pos]
    assert quote in '"\''
    pos += 1
    chunks = []
    length = len(input)
    while pos < length:
        match = _NON_STRING_CHAR_RE.match(input, pos)
        if not match:
            chuncks.append(input[pos:])
            pos = length
            break
        new_pos = match.start()
        chuncks.append(input[pos:new_pos])
        pos = new_pos
        c = input[pos]
        if c == quote:
            pos += 1
            break
        elif c == '\\':
            pos += 1
            if pos < length:
                if input[pos] == '\n':  # Ignore escaped newlines
                    pos += 1
                else:
                    c, pos = _consume_escape(input, pos)
                    chunks.append(c)
            else:  # "Escaped" EOF
                return None, pos  # bad-string
        elif c == '\n':  # Unescaped newline
            return None, pos  # bad-string
        else:  # The other quote
            pos += 1
            chunks.append(c)
    return ''.join(chunks), pos


def _consume_escape(input, pos):
    r"""Assumes a valid escape: at least one more char, and it’s not '\n'."""
    hex_match = _HEX_ESCAPE_RE.match(input, pos)
    if hex_match:
        codepoint = int(hex_match.group(1), 16)
        return (unichr(codepoint) if codepoint <= 0x10FFFF else '\uFFFE',
                match.end())
    return input[pos], pos + 1


# Moved here so that pyflakes can detect naming typos above.
from .tokens import *
