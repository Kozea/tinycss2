from . import color4

COLOR_SPACES = color4.COLOR_SPACES | {'device-cmyk'}
D50 = color4.D50
D65 = color4.D65


class Color(color4.Color):
    COLOR_SPACES = None


def parse_color(input):
    color = color4.parse_color(input)

    if color:
        return color

    if isinstance(input, str):
        token = color4.parse_one_component_value(input, skip_comments=True)
    else:
        token = input

    if token.type == 'function':
        tokens = [
            token for token in token.arguments
            if token.type not in ('whitespace', 'comment')]
        name = token.lower_name

        if name == 'color':
            space, *tokens = tokens

        length = len(tokens)

        if length in (7, 9) and all(token == ',' for token in tokens[1::2]):
            old_syntax = True
            tokens = tokens[::2]
        elif length in (3, 4):
            old_syntax = False
        elif length == 6 and tokens[4] == '/':
            tokens.pop(4)
            old_syntax = False
        else:
            return
        args, alpha = tokens[:4], color4._parse_alpha(tokens[4:])

        if name == 'device-cmyk':
            return _parse_device_cmyk(args, alpha, old_syntax)
        elif name == 'color' and not old_syntax:
            return _parse_color(space, args, alpha)


def _parse_device_cmyk(args, alpha, old_syntax):
    """Parse a list of CMYK channels.

    If args is a list of 4 NUMBER or PERCENTAGE tokens, return
    device-cmyk :class:`Color`. Otherwise, return None.

    Input C, M, Y, K ranges are [0, 1], output are [0, 1].

    """
    if old_syntax:
        if color4._types(args) != {'number'}:
            return
    else:
        if not color4._types(args) <= {'numbers', 'percentage'}:
            return
    cmyk = [
        arg.value if arg.type == 'number' else
        arg.value / 100 if arg.type == 'percentage' else None
        for arg in args]
    return Color('device-cmyk', cmyk, alpha)


def _parse_color(space, args, alpha):
    """Parse a color space name list of coordinates.

    Ranges are [0, 1].

    """
    if not color4._types(args) <= {'number', 'percentage'}:
        return
    if space.type != 'ident' or not space.value.startswith('--'):
        return
    coordinates = [
        arg.value if arg.type == 'number' else
        arg.value / 100 if arg.type == 'percentage' else None
        for arg in args]
    return Color(space.value, coordinates, alpha)
