if str is bytes:  # pragma: no cover
    unichr = unichr  # noqa
    basestring = basestring  # noqa
else:  # pragma: no cover
    unichr = chr  # noqa
    basestring = str  # noqa
