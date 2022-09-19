from colorsys import hls_to_rgb
from math import cos, sin, tau

from .color3 import (
    _BASIC_COLOR_KEYWORDS, _EXTENDED_COLOR_KEYWORDS, _HASH_REGEXPS)
from .parser import parse_one_component_value


class Color:
    """A specified color in a defined color space.

    The color space is ``srgb``, ``srgb-linear``, ``display-p3``, ``a98-rgb``,
    ``prophoto-rgb``, ``rec2020``, ``xyz-d50`` or ``xyz-d65``.

    The alpha channel is clipped to [0, 1] but params have undefined range.

    For example, ``rgb(-10%, 120%, 0%)`` is represented as
    ``'srgb', (-0.1, 1.2, 0, 1), 1``.

    """
    def __init__(self, space, params, alpha=1):
        self.space = space
        self.params = tuple(float(param) for param in params)
        self.alpha = float(alpha)

    def __repr__(self):
        params = ' '.join(str(param) for param in self.params)
        return f'color({self.space} {params} / {self.alpha})'

    def __iter__(self):
        yield from self.params
        yield self.alpha

    def __getitem__(self, key):
        return (self.params + (self.alpha,))[key]

    def __hash__(self):
        return hash(f'{self.space}{self.params}{self.alpha}')

    def __eq__(self, other):
        return (
            tuple(self) == other if isinstance(other, tuple)
            else super().__eq__(other))


def srgb(red, green, blue, alpha=1):
    """Create a :class:`Color` whose color space is sRGB."""
    return Color('srgb', (red, green, blue), alpha)


def parse_color(input):
    """Parse a color value as defined in CSS Color Level 4.

    https://www.w3.org/TR/css-color-4/

    Implementation of Level 4 is currently limited to space-seperated arguments
    with an optional slash-seperated opacity, definition of 'rebeccapurple',
    percentages and numbers are accepted as opacity values, the hwb() function,
    and hsla()/rgba() being aliases to hsl()/rgb().

    :type input: :obj:`str` or :term:`iterable`
    :param input: A string or an iterable of :term:`component values`.
    :returns:
        * :obj:`None` if the input is not a valid color value.
          (No exception is raised.)
        * The string ``'currentColor'`` for the ``currentColor`` keyword
        * A :class:`SRGB` object for colors whose color space is sRGB
        * A :class:`Color` object for every other values, including keywords.

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
                    channels.append(1)
                return srgb(*channels)
    elif token.type == 'function':
        tokens = [
            token for token in token.arguments
            if token.type not in ('whitespace', 'comment')]
        length = len(tokens)
        if length in (5, 7) and all(token == ',' for token in tokens[1::2]):
            old_syntax = True
            tokens = tokens[::2]
        elif length == 3:
            old_syntax = False
        elif length == 5 and tokens[3] == '/':
            tokens.pop(3)
            old_syntax = False
        else:
            return
        name = token.lower_name
        args, alpha = tokens[:3], _parse_alpha(tokens[3:])
        if alpha is None:
            return
        if name in ('rgb', 'rgba'):
            return _parse_rgb(args, alpha)
        elif name in ('hsl', 'hsla'):
            return _parse_hsl(args, alpha)
        elif name == 'hwb':
            return _parse_hwb(args, alpha)
        elif name == 'lab' and not old_syntax:
            return _parse_lab(args, alpha)
        elif name == 'lch' and not old_syntax:
            return _parse_lch(args, alpha)
        elif name == 'oklab' and not old_syntax:
            return _parse_oklab(args, alpha)
        elif name == 'oklch' and not old_syntax:
            return _parse_oklch(args, alpha)


def _parse_alpha(args):
    """Parse a list of one alpha value.

    If args is a list of a single INTEGER, NUMBER or PERCENTAGE token,
    return its value clipped to the 0..1 range. Otherwise, return None.

    """
    if len(args) == 0:
        return 1.
    elif len(args) == 1:
        if args[0].type == 'number':
            return min(1, max(0, args[0].value))
        elif args[0].type == 'percentage':
            return min(1, max(0, args[0].value / 100))


def _parse_rgb(args, alpha):
    """Parse a list of RGB channels.

    If args is a list of 3 NUMBER tokens or 3 PERCENTAGE tokens, return
    sRGB :class:`Color`. Otherwise, return None.

    """
    types = [arg.type for arg in args]
    if types == ['number', 'number', 'number']:
        return srgb(*[arg.value / 255 for arg in args], alpha)
    elif types == ['percentage', 'percentage', 'percentage']:
        return srgb(*[arg.value / 100 for arg in args], alpha)


def _parse_hsl(args, alpha):
    """Parse a list of HSL channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 PERCENTAGE tokens,
    return sRGB :class:`Color`. Otherwise, return None.

    """
    if (args[1].type, args[2].type) != ('percentage', 'percentage'):
        return
    hue = _parse_hue(args[0])
    if hue is None:
        return
    r, g, b = hls_to_rgb(hue, args[2].value / 100, args[1].value / 100)
    return srgb(r, g, b, alpha)


def _parse_hwb(args, alpha):
    """Parse a list of HWB channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 PERCENTAGE tokens,
    return sRGB :class:`Color`. Otherwise, return None.

    """
    if (args[1].type, args[2].type) != ('percentage', 'percentage'):
        return
    hue = _parse_hue(args[0])
    if hue is None:
        return
    white, black = (arg.value / 100 for arg in args[1:])
    if white + black >= 1:
        gray = white / (white + black)
        return srgb(gray, gray, gray, alpha)
    else:
        rgb = hls_to_rgb(hue, 0.5, 1)
        r, g, b = ((channel * (1 - white - black)) + white for channel in rgb)
        return srgb(r, g, b, alpha)


def _parse_lab(args, alpha):
    """Parse a list of CIE Lab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return xyz-d50
    :class:`Color`. Otherwise, return None.

    """
    if len(args) != 3 or {arg.type for arg in args} > {'number', 'percentage'}:
        return
    L = args[0].value
    a = args[1].value * (1 if args[1].type == 'number' else 1.25)
    b = args[2].value * (1 if args[2].type == 'number' else 1.25)
    return Color('xyz-d50', _lab_to_xyz(L, a, b), alpha)


def _parse_lch(args, alpha):
    """Parse a list of CIE LCH channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return xyz-d50 :class:`Color`. Otherwise, return None.

    """
    if len(args) != 3:
        return
    if {args[0].type, args[1].type} > {'number', 'percentage'}:
        return
    L = args[0].value
    C = args[1].value * (1 if args[1].type == 'number' else 1.5)
    H = _parse_hue(args[2])
    if H is None:
        return
    a = C * cos(H * tau)
    b = C * sin(H * tau)
    return Color('xyz-d50', _lab_to_xyz(L, a, b), alpha)


def _lab_to_xyz(L, a, b):
    # Code from https://www.w3.org/TR/css-color-4/#color-conversion-code
    κ = 24389 / 27
    ε = 216 / 24389
    f1 = (L + 16) / 116
    f0 = a / 500 + f1
    f2 = f1 - b / 200
    X = (f0 ** 3 if f0 ** 3 > ε else (116 * f0 - 16) / κ) * 0.3457 / 0.3585
    Y = (((L + 16) / 116) ** 3 if L > κ * ε else L / κ)
    Z = (f2 ** 3 if f2 ** 3 > ε else (116 * f2 - 16) / κ) * 0.2958 / 0.3585
    return X, Y, Z


def _parse_oklab(args, alpha):
    """Parse a list of OKLab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return xyz-d65
    :class:`Color`. Otherwise, return None.

    """
    if len(args) != 3 or {arg.type for arg in args} > {'number', 'percentage'}:
        return
    L = args[0].value
    a = args[1].value * (1 if args[1].type == 'number' else 0.004)
    b = args[2].value * (1 if args[2].type == 'number' else 0.004)
    return Color('xyz-d65', _oklab_to_xyz(L, a, b), alpha)


def _parse_oklch(args, alpha):
    """Parse a list of OKLCH channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return xyz-d65 :class:`Color`. Otherwise, return None.

    """
    if len(args) != 3 or (
            {args[0].type, args[1].type} > {'number', 'percentage'}):
        return
    L = args[0].value
    C = args[1].value * (1 if args[1].type == 'number' else 1.5)
    H = _parse_hue(args[2])
    if H is None:
        return
    a = C * cos(H * tau)
    b = C * sin(H * tau)
    return Color('xyz-d65', _oklab_to_xyz(L, a, b), alpha)


def _oklab_to_xyz(L, a, b):
    # Code from https://www.w3.org/TR/css-color-4/#color-conversion-code
    lab = (L / 100, a, b)
    lms = [
        sum(_OKLAB_TO_LMS[i][j] * lab[j] for j in range(3)) for i in range(3)]
    X, Y, Z = [
        sum(_LMS_TO_XYZ[i][j] * lms[j]**3 for j in range(3)) for i in range(3)]
    return X, Y, Z


def _parse_hue(token):
    if token.type == 'number':
        return token.value / 360
    elif token.type == 'dimension':
        if token.unit == 'deg':
            return token.value / 360
        elif token.unit == 'grad':
            return token.value / 400
        elif token.unit == 'rad':
            return token.value / tau
        elif token.unit == 'turn':
            return token.value


# (r, g, b) in 0..255
_EXTENDED_COLOR_KEYWORDS = _EXTENDED_COLOR_KEYWORDS.copy()
_EXTENDED_COLOR_KEYWORDS.append(('rebeccapurple', (102, 51, 153)))


# (r, g, b, a) in 0..1 or a string marker
_SPECIAL_COLOR_KEYWORDS = {
    'currentcolor': 'currentColor',
    'transparent': srgb(0, 0, 0, 0),
}


# RGBA named tuples of (r, g, b, a) in 0..1 or a string marker
_COLOR_KEYWORDS = _SPECIAL_COLOR_KEYWORDS.copy()
_COLOR_KEYWORDS.update(
    # 255 maps to 1, 0 to 0, the rest is linear.
    (keyword, srgb(red / 255, green / 255, blue / 255, 1))
    for keyword, (red, green, blue)
    in _BASIC_COLOR_KEYWORDS + _EXTENDED_COLOR_KEYWORDS)


# Transformation matrices for OKLab
_LMS_TO_XYZ = (
    (1.2268798733741557, -0.5578149965554813, 0.28139105017721583),
    (-0.04057576262431372, 1.1122868293970594, -0.07171106666151701),
    (-0.07637294974672142, -0.4214933239627914, 1.5869240244272418),
)
_OKLAB_TO_LMS = (
    (0.99999999845051981432, 0.39633779217376785678, 0.21580375806075880339),
    (1.0000000088817607767, -0.1055613423236563494, -0.063854174771705903402),
    (1.0000000546724109177, -0.089484182094965759684, -1.2914855378640917399),
)
