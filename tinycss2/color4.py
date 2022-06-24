from colorsys import hls_to_rgb

from .color3 import (
    _BASIC_COLOR_KEYWORDS, _EXTENDED_COLOR_KEYWORDS, _HASH_REGEXPS,
    _SPECIAL_COLOR_KEYWORDS, RGBA, _parse_hsl, _parse_rgb)
from .parser import parse_one_component_value


def parse_color(input):
    """Parse a color value as defined in `CSS Color Level 4
    <https://www.w3.org/TR/css-color-4/>`. Implementation of Level 4
    is currently limited to space-seperated arguments with an optional
    slash-seperated opacity, definition of 'rebeccapurple',
    percentages and numbers are accepted as opacity values,
    the hwb() function and hsla()/rgba() being aliases to hsl()/rgb().

    :type input: :obj:`str` or :term:`iterable`
    :param input: A string or an iterable of :term:`component values`.
    :returns:
        * :obj:`None` if the input is not a valid color value.
          (No exception is raised.)
        * The string ``'currentColor'`` for the ``currentColor`` keyword
        * Or a :class:`RGBA` object for every other values
          (including keywords, HSL and HSLA.)
          The alpha channel is clipped to [0, 1]
          but red, green, or blue can be out of range
          (eg. ``rgb(-10%, 120%, 0%)`` is represented as
          ``(-0.1, 1.2, 0, 1)``.)

    """
    if isinstance(input, str):
        token = parse_one_component_value(input, skip_comments=True)
    else:
        token = input
    if token.type == 'ident':
        return _COLOR_KEYWORDS.get(token.lower_value)
    elif token.type == 'hash':
        for multiplier, regexp in _HASH_REGEXPS:
            match = regexp(token.value)
            if match:
                channels = [
                    int(group * multiplier, 16) / 255
                    for group in match.groups()]
                if len(channels) == 3:
                    channels.append(1.)
                return RGBA(*channels)
    elif token.type == 'function':
        args = _parse_separated_args(token.arguments)
        if args:
            name = token.lower_name
            if name == 'rgb' or name == 'rgba':
                alpha = _parse_alpha(args[3:])
                if alpha is not None:
                    return _parse_rgb(args[:3], alpha)
                else:
                    return _parse_rgb(args, alpha=1.)
            elif name == 'hsl' or name == 'hsla':
                alpha = _parse_alpha(args[3:])
                if alpha is not None:
                    return _parse_hsl(args[:3], alpha)
                else:
                    return _parse_hsl(args, alpha=1.)
            elif name == 'hwb':
                alpha = _parse_alpha(args[3:])
                if alpha is not None:
                    return _parse_hwb(args[:3], alpha)
                else:
                    return _parse_hwb(args, alpha=1.)


def _parse_separated_args(tokens):
    """Parse a list of tokens (typically the content of a function token)
    as arguments made of a single token each, either comma seperated or
    space-seperated with an optional slash-seperated opacity.

    return the argument list without commas or white space;
    or None if the function token content do not match the description above.

    """
    tokens = [token for token in tokens
              if token.type not in ('whitespace', 'comment')]
    if len(tokens) % 2 == 1 and all(token == ',' for token in tokens[1::2]):
        return tokens[::2]
    elif len(tokens) == 3 and all(
            token.type in ('number', 'percentage') for token in tokens):
        return tokens
    elif len(tokens) == 5 and tokens[3] == '/':
        args = [token for token in tokens if token != '/']
        return args


def _parse_alpha(args):
    """Parse a list of one alpha value.

    If args is a list of a single INTEGER, NUMBER or PERCENTAGE token,
    return its value clipped to the 0..1 range. Otherwise, return None.

    """
    if len(args) == 1 and args[0].type == 'number':
        return min(1, max(0, args[0].value))
    if len(args) == 1 and args[0].type == 'percentage':
        return min(1, max(0, args[0].value/100))


def _parse_hwb(args, alpha):
    """Parse a list of HWB channels.

    If args is a list of 1 INTEGER token and 2 PERCENTAGE tokens, return RGB
    values as a tuple of 3 floats in 0..1. Otherwise, return None.

    """
    types = [arg.type for arg in args]
    if types == ['number', 'percentage', 'percentage'] and args[0].is_integer:
        white = args[1].value / 100
        black = args[2].value / 100
        if white + black >= 1:
            gray = white / (white + black)
            return RGBA(gray, gray, gray, alpha)
        else:
            rgb = hls_to_rgb(args[0].int_value / 360, 0.5, 1)
            r, g, b = ((channel * (1 - white - black)) + white
                       for channel in rgb)
            return RGBA(r, g, b, alpha)


# (r, g, b) in 0..255
_EXTENDED_COLOR_KEYWORDS.insert(119, ('rebeccapurple', (102, 51, 153)))

# RGBA named tuples of (r, g, b, a) in 0..1 or a string marker
_COLOR_KEYWORDS = _SPECIAL_COLOR_KEYWORDS.copy()
_COLOR_KEYWORDS.update(
    # 255 maps to 1, 0 to 0, the rest is linear.
    (keyword, RGBA(r / 255., g / 255., b / 255., 1.))
    for keyword, (r, g, b) in _BASIC_COLOR_KEYWORDS + _EXTENDED_COLOR_KEYWORDS)
