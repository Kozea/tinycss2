from colorsys import hls_to_rgb
from math import cbrt, cos, sin, tau

from .color3 import _BASIC_COLOR_KEYWORDS, _EXTENDED_COLOR_KEYWORDS, _HASH_REGEXPS
from .parser import parse_one_component_value

# Code adapted from https://www.w3.org/TR/css-color-4/#color-conversion-code.
κ = 24389 / 27
ε = 216 / 24389
D50 = (0.3457 / 0.3585, 1, (1 - 0.3457 - 0.3585) / 0.3585)
D65 = (0.3127 / 0.3290, 1, (1 - 0.3127 - 0.3290) / 0.3290)
SPACES = {
    'srgb', 'srgb-linear',
    'display-p3', 'a98-rgb', 'prophoto-rgb', 'rec2020',
    'xyz', 'xyz-d50', 'xyz-d65'
}
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


def xyz_to_lab(X, Y, Z, d=(1, 1, 1)):
    x = X / d[0]
    y = Y / d[1]
    z = Z / d[2]
    f0 = cbrt(x) if x > ε else (κ * x + 16) / 116
    f1 = cbrt(y) if y > ε else (κ * y + 16) / 116
    f2 = cbrt(z) if z > ε else (κ * z + 16) / 116
    L = (116 * f1) - 16
    a = 500 * (f0 - f1)
    b = 200 * (f1 - f2)
    return L, a, b


def lab_to_xyz(L, a, b, d=(1, 1, 1)):
    f1 = (L + 16) / 116
    f0 = a / 500 + f1
    f2 = f1 - b / 200
    x = (f0 ** 3 if f0 ** 3 > ε else (116 * f0 - 16) / κ)
    y = (((L + 16) / 116) ** 3 if L > κ * ε else L / κ)
    z = (f2 ** 3 if f2 ** 3 > ε else (116 * f2 - 16) / κ)
    X = x * d[0]
    Y = y * d[1]
    Z = z * d[2]
    return X, Y, Z


def _oklab_to_xyz(L, a, b):
    lab = (L, a, b)
    lms = [sum(_OKLAB_TO_LMS[i][j] * lab[j] for j in range(3)) for i in range(3)]
    X, Y, Z = [sum(_LMS_TO_XYZ[i][j] * lms[j]**3 for j in range(3)) for i in range(3)]
    return X, Y, Z


class Color:
    """A specified color in a defined color space.

    The color space is ``srgb``, ``srgb-linear``, ``display-p3``, ``a98-rgb``,
    ``prophoto-rgb``, ``rec2020``, ``xyz-d50`` or ``xyz-d65``.

    The alpha channel is clipped to [0, 1] but params have undefined range.

    For example, ``rgb(-10%, 120%, 0%)`` is represented as
    ``'srgb', (-0.1, 1.2, 0, 1), 1``.

    Original values, used for interpolation, are stored in ``function_names``
    and ``args``.

    """
    def __init__(self, function_name, args, space, params, alpha):
        self.function_name = function_name
        self.args = args
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
        return (*self.params, self.alpha)[key]

    def __hash__(self):
        return hash(f'{self.space}{self.params}{self.alpha}')

    def __eq__(self, other):
        if isinstance(other, str):
            return False
        elif isinstance(other, tuple):
            return tuple(self) == other
        elif isinstance(other, Color):
            return self.space == other.space and self.params == other.params
        return super().__eq__(other)


def parse_color(input):
    """Parse a color value as defined in CSS Color Level 4.

    https://www.w3.org/TR/css-color-4/

    :type input: :obj:`str` or :term:`iterable`
    :param input: A string or an iterable of :term:`component values`.
    :returns:
        * :obj:`None` if the input is not a valid color value.
          (No exception is raised.)
        * The string ``'currentColor'`` for the ``currentColor`` keyword
        * A :class:`Color` object for every other values, including keywords.

    """
    if isinstance(input, str):
        token = parse_one_component_value(input, skip_comments=True)
    else:
        token = input
    if token.type == 'ident':
        if token.lower_value == 'currentcolor':
            return 'currentColor'
        elif token.lower_value == 'transparent':
            return Color('rgb', (0, 0, 0), 'srgb', (0, 0, 0), 0)
        elif color := _COLOR_KEYWORDS.get(token.lower_value):
            rgb = tuple(channel / 255 for channel in color)
            return Color('rgb', rgb, 'srgb', rgb, 1)
    elif token.type == 'hash':
        for multiplier, regexp in _HASH_REGEXPS:
            match = regexp(token.value)
            if match:
                channels = [
                    int(group * multiplier, 16) / 255
                    for group in match.groups()]
                alpha = channels.pop() if len(channels) == 4 else 1
                return Color('rgb', channels, 'srgb', channels, alpha)
    elif token.type == 'function':
        tokens = [
            token for token in token.arguments
            if token.type not in ('whitespace', 'comment')]
        name = token.lower_name
        if name == 'color':
            space, *tokens = tokens
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
        elif name == 'color' and not old_syntax:
            return _parse_color(space, args, alpha)


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
    values = [arg.value for arg in args]
    for i, arg in enumerate(args):
        if arg.type == 'ident' and arg.lower_value == 'none':
            types[i] = 'number' if 'number' in types else 'percentage'
            values[i] = 0
    if types == ['number', 'number', 'number']:
        params = tuple(value / 255 for value in values)
    elif types == ['percentage', 'percentage', 'percentage']:
        params = tuple(value / 100 for value in values)
    else:
        return
    args = [None if arg.type == 'ident' else param for arg, param in zip(args, params)]
    return Color('rgb', args, 'srgb', params, alpha)


def _parse_hsl(args, alpha):
    """Parse a list of HSL channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 PERCENTAGE tokens,
    return sRGB :class:`Color`. Otherwise, return None.

    """
    values = [arg.value for arg in args]
    for i in (1, 2):
        if args[i].type == 'ident' and args[i].lower_value == 'none':
            values[i] = 0
        elif args[i].type != 'percentage':
            return
    values[0] = _parse_hue(args[0])
    if values[0] is None:
        return
    values[1] /= 100
    values[2] /= 100
    args = [None if arg.type == 'ident' else value for arg, value in zip(args, values)]
    params = hls_to_rgb(values[0], values[2], values[1])
    return Color('hsl', args, 'srgb', params, alpha)


def _parse_hwb(args, alpha):
    """Parse a list of HWB channels.

    If args is a list of 1 NUMBER or ANGLE token and 2 PERCENTAGE tokens,
    return sRGB :class:`Color`. Otherwise, return None.

    """
    values = [arg.value for arg in args]
    for i in (1, 2):
        if args[i].type == 'ident' and args[i].lower_value == 'none':
            values[i] = 0
        elif args[i].type != 'percentage':
            return
    values[0] = _parse_hue(args[0])
    if values[0] is None:
        return
    values[1:] = (value / 100 for value in values[1:])
    args = [None if arg.type == 'ident' else value for arg, value in zip(args, values)]
    white, black = values[1:]
    if white + black >= 1:
        params = (white / (white + black),) * 3
    else:
        rgb = hls_to_rgb(values[0], 0.5, 1)
        params = ((channel * (1 - white - black)) + white for channel in rgb)
    return Color('hwb', args, 'srgb', params, alpha)


def _parse_lab(args, alpha):
    """Parse a list of CIE Lab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return xyz-d50
    :class:`Color`. Otherwise, return None.

    """
    values = [arg.value for arg in args]
    for i in range(3):
        if args[i].type == 'ident':
            if args[i].lower_value == 'none':
                values[i] = 0
            else:
                return
        elif args[i].type not in ('percentage', 'number'):
            return
    L = values[0]
    a = values[1] * (1 if args[1].type == 'number' else 1.25)
    b = values[2] * (1 if args[2].type == 'number' else 1.25)
    args = [
        None if args[0].type == 'ident' else L / 100,
        None if args[1].type == 'ident' else a / 125,
        None if args[2].type == 'ident' else b / 125,
    ]
    xyz = lab_to_xyz(L, a, b, D50)
    return Color('lab', args, 'xyz-d50', xyz, alpha)


def _parse_lch(args, alpha):
    """Parse a list of CIE LCH channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return xyz-d50 :class:`Color`. Otherwise, return None.

    """
    values = [arg.value for arg in args]
    for i in range(2):
        if args[i].type == 'ident':
            if args[i].lower_value == 'none':
                values[i] = 0
            else:
                return
        elif args[i].type not in ('percentage', 'number'):
            return
    L = values[0]
    C = values[1] * (1 if args[1].type == 'number' else 1.5)
    H = _parse_hue(args[2])
    if H is None:
        return
    args = [
        None if args[0].type == 'ident' else L / 100,
        None if args[1].type == 'ident' else C / 150,
        None if args[2].type == 'ident' else H,
    ]
    a = C * cos(H * tau)
    b = C * sin(H * tau)
    xyz = lab_to_xyz(L, a, b, D50)
    return Color('lch', args, 'xyz-d50', xyz, alpha)


def _parse_oklab(args, alpha):
    """Parse a list of OKLab channels.

    If args is a list of 3 NUMBER or PERCENTAGE tokens, return xyz-d65
    :class:`Color`. Otherwise, return None.

    """
    values = [arg.value for arg in args]
    for i in range(3):
        if args[i].type == 'ident':
            if args[i].lower_value == 'none':
                values[i] = 0
            else:
                return
        elif args[i].type not in ('percentage', 'number'):
            return
    L = values[0] * (1 if args[0].type == 'number' else (1 / 100))
    a = values[1] * (1 if args[1].type == 'number' else (0.4 / 100))
    b = values[2] * (1 if args[2].type == 'number' else (0.4 / 100))
    args = [
        None if args[0].type == 'ident' else L,
        None if args[1].type == 'ident' else a / 0.4,
        None if args[2].type == 'ident' else b / 0.4,
    ]
    xyz = _oklab_to_xyz(L, a, b)
    return Color('oklab', args, 'xyz-d65', xyz, alpha)


def _parse_oklch(args, alpha):
    """Parse a list of OKLCH channels.

    If args is a list of 2 NUMBER or PERCENTAGE tokens and 1 NUMBER or ANGLE
    token, return xyz-d65 :class:`Color`. Otherwise, return None.

    """
    if {args[0].type, args[1].type} > {'number', 'percentage'}:
        return
    values = [arg.value for arg in args]
    for i in range(2):
        if args[i].type == 'ident':
            if args[i].lower_value == 'none':
                values[i] = 0
            else:
                return
        elif args[i].type not in ('percentage', 'number'):
            return
    L = values[0] * (1 if args[0].type == 'number' else (1 / 100))
    C = values[1] * (1 if args[1].type == 'number' else (0.4 / 100))
    H = _parse_hue(args[2])
    if H is None:
        return
    args = [
        None if args[0].type == 'ident' else L,
        None if args[1].type == 'ident' else C / 0.4,
        None if args[2].type == 'ident' else H,
    ]
    a = C * cos(H * tau)
    b = C * sin(H * tau)
    xyz = _oklab_to_xyz(L, a, b)
    return Color('oklch', args, 'xyz-d65', xyz, alpha)


def _parse_color(space, args, alpha):
    """Parse a color space name list of channels."""
    values = [arg.value for arg in args]
    for i in range(3):
        if args[i].type == 'ident':
            if args[i].lower_value == 'none':
                values[i] = 0
            else:
                return
        elif args[i].type == 'percentage':
            values[i] /= 100
        elif args[i].type != 'number':
            return
    args = [
        None if args[0].type == 'ident' else values[0],
        None if args[1].type == 'ident' else values[1],
        None if args[2].type == 'ident' else values[2],
    ]
    if space.type == 'ident' and (space := space.lower_value) in SPACES:
        return Color('color', args, space, values, alpha)


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
    elif token.type == 'ident' and token.lower_value == 'none':
        return 0


# (r, g, b) in 0..255
_EXTENDED_COLOR_KEYWORDS = _EXTENDED_COLOR_KEYWORDS.copy()
_EXTENDED_COLOR_KEYWORDS.append(('rebeccapurple', (102, 51, 153)))
_COLOR_KEYWORDS = dict(_BASIC_COLOR_KEYWORDS + _EXTENDED_COLOR_KEYWORDS)
