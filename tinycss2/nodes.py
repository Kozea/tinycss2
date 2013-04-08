class _Node(object):
    """Base class for all nodes.

    They have different name and categorization,
    but nodes and tokens have the same attributes.

    """
    __slots__ = ['source_line', 'source_column']

    def __init__(self, line, column):
        self.source_line = line
        self.source_column = column


class Declaration(_Node):
    """A CSS (property or descriptor) declaration.

    Syntax:
    ``<ident> <whitespace>* ':' <token>* ( '!' <ident("important")> )?``

    .. attribute:: name

        The unescaped value, as an Unicode string.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_name

        Same as :attr:`name`, but with the original casing preserved.

    .. attribute:: value

        The declaration value as a list of tokens:
        anything between ``:`` and
        the end of the declaration, or ``!important``.

    .. attribute:: important

        A boolean, true if the declaration had an ``!important`` markers.
        It is up to the consumer to reject declarations that do not accept
        this flag, such as non-property descriptor declarations.

    """
    __slots__ = ['name', 'case_sensitive_name', 'value', 'important']
    type = 'declaration'

    def __init__(self, line, column,
                 name, case_sensitive_name, value, important):
        _Node.__init__(self, line, column)
        self.name = name
        self.case_sensitive_name = case_sensitive_name
        self.value = value
        self.important = important


class QualifiedRule(_Node):
    """A CSS qualified rule, ie. a rule that is not an at-rule.

    Qulified rules are often style rules,
    where the head is parsed as a selector list
    and the body as a declaration list.

    Syntax:
    ``<token except {} block>* <{} block>``

    .. attribute:: head

        The rule’s head, the part before the {} block, as a list of tokens.

    .. attribute:: body

        The rule’s body, the part inside the {} block, as a list of tokens.

    """
    __slots__ = ['head', 'body']
    type = 'qualified-rule'

    def __init__(self, line, column, head, body):
        _Node.__init__(self, line, column)
        self.head = head
        self.body = body


class AtRule(_Node):
    """A CSS at-rule.

    The interpretation of at-rules depend on their at-keywords.
    Most at-rules (ie. at-keyword values) are only allowed in some context,
    and must either end with a {} block or a ``;``.

    Syntax:
    ``<at-keyword> <token except {} block>* ( <{} block> | ';' )``

    .. attribute:: at_keyword

        The unescaped value of the rule’s at-keyword,
        without the ``@`` symbol, as an Unicode string.
        Normalized to *ASCII lower case*; see :func:`~tinycss2.ascii_lower`.

    .. attribute:: case_sensitive_at_keyword

        Same as :attr:`at_keyword`, but with the original casing preserved.

    .. attribute:: head

        The rule’s head, the part before the {} block or the ``;``,
        as a list of tokens.

    .. attribute:: body

        The rule’s body, if any.
        The block’s content as a list of tokens for at-rules with a {} block.
        :obj:`None` for at-rules ending with ``;``.

    """
    __slots__ = ['head', 'body']
    type = 'at-rule'

    def __init__(self, line, column,
                 at_keyword, case_sensitive_at_keyword, head, body):
        _Node.__init__(self, line, column)
        self.at_keyword = at_keyword
        self.case_sensitive_at_keyword = case_sensitive_at_keyword
        self.head = head
        self.body = body
