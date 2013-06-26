if str is bytes:  # pragma: no cover
    # Python 2
    unichr = unichr
    basestring = basestring
else:
    unichr = chr
    basestring = str
