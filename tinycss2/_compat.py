if str is bytes:  # Python 2
    unichr = unichr
    basestring = basestring
else:
    unichr = chr
    basestring = str
