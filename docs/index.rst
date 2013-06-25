.. currentmodule:: tinycss2.ast

.. glossary::

    String
        An Unicode string.
        (:class:`str` on Python 3.x, :class:`unicode` on Python 2.x.)
        On Python 2.x, a byte string (:class:`str`)
        contaning only ASCII characters is also accepted and implicitly decoded.

    Component value
        A :term:`preserved token`
        or a :class:`ParenthesesBlock`,
        :class:`SquareBracketsBlock`,
        :class:`CurlyBracketsBlock`,
        :class:`Function`,
        or :class:`ParseError` object.

    Preserved token
        A :class:`WhitespaceToken`,
        :class:`LiteralToken`,
        :class:`IdentToken`,
        :class:`AtKeywordToken`,
        :class:`HashToken`,
        :class:`StringToken`,
        :class:`URLToken`,
        :class:`NumberToken`,
        :class:`PercentageToken`,
        :class:`DimensionToken`,
        :class:`UnicodeRangeToken`,
        or (if requested explicitly) :class:`Comment` object.
