API Reference
=============


Parsing
-------

tinycss2 is “low-level” in that it doesn’t parse all of CSS: it doesn’t know
about the syntax of any specific properties or at-rules. Instead, it provides
a set of functions that can be composed to support exactly the parts of CSS
you’re interested in, including new or non-standard rules or properties,
without modifying tinycss2 or having a complex hook/plugin system.

In many cases, parts of the parsed values (such as the
:attr:`~tinycss2.ast.AtRule.content` of a :class:`~tinycss2.ast.AtRule`) is
given as :term:`component values` that can be parsed further with other
functions.

.. module:: tinycss2
.. autofunction:: parse_stylesheet_bytes
.. autofunction:: parse_stylesheet
.. autofunction:: parse_rule_list
.. autofunction:: parse_one_rule
.. autofunction:: parse_blocks_contents
.. autofunction:: parse_declaration_list
.. autofunction:: parse_one_declaration
.. autofunction:: parse_component_value_list
.. autofunction:: parse_one_component_value


Serialization
-------------

In addition to each node’s a :meth:`~tinycss2.ast.Node.serialize` method, some
serialization-related functions are available:

.. autofunction:: serialize
.. autofunction:: serialize_identifier


.. module:: tinycss2.color3


Color
-----

.. autofunction:: parse_color
.. autoclass:: RGBA


.. module:: tinycss2.nth


<An+B>
------

.. autofunction:: parse_nth


.. module:: tinycss2.ast


AST nodes
---------

Various parsing functions return a **node** or a list of nodes. Some types of
nodes contain nested nodes which may in turn contain more nodes, forming
together an **abstract syntax tree**.

Although you typically don’t need to import it, the :mod:`tinycss2.ast` module
defines a class for every type of node.

.. autoclass:: Node()

.. autoclass:: QualifiedRule()
.. autoclass:: AtRule()
.. autoclass:: Declaration()

.. autoclass:: ParseError()
.. autoclass:: Comment()
.. autoclass:: WhitespaceToken()
.. autoclass:: LiteralToken()
.. autoclass:: IdentToken()
.. autoclass:: AtKeywordToken()
.. autoclass:: HashToken()
.. autoclass:: StringToken()
.. autoclass:: URLToken()
.. autoclass:: UnicodeRangeToken()
.. autoclass:: NumberToken()
.. autoclass:: PercentageToken()
.. autoclass:: DimensionToken()
.. autoclass:: ParenthesesBlock()
.. autoclass:: SquareBracketsBlock()
.. autoclass:: CurlyBracketsBlock()
.. autoclass:: FunctionBlock()


Glossary
--------

.. currentmodule:: tinycss2.ast
.. glossary::

    component value
    component values
        A :class:`ParseError`,
        :class:`WhitespaceToken`,
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
        :class:`ParenthesesBlock`,
        :class:`SquareBracketsBlock`,
        :class:`CurlyBracketsBlock`,
        :class:`FunctionBlock`,
        or :class:`Comment`
        object.
