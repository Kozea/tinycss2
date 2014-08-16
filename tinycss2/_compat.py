if str is bytes:  # pragma: no cover
    unichr = unichr
    basestring = basestring
else:  # pragma: no cover
    unichr = chr
    basestring = str
