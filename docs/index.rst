.. include:: ../README.rst

Contents:

.. toctree::
   :maxdepth: 2


Installation
============

Installing tinycss2 with pip_ should Just Work::

    pip install tinycss2

This will also automatically install tinycss2’s only dependency, webencodings_.
tinycss2 and webencodings both only contain Python code
and should work on any Python implementation,
although they’re only tested on CPython and PyPy.

.. _pip: http://pip-installer.org/
.. _webencodings: http://pythonhosted.org/webencodings/


.. _parsing:

Parsing overview
================

Various parsing functions return a **node** or a list of nodes.
Some types of nodes contain nested nodes which may in turn contain more nodes,
forming together an **abstract syntax tree**.


.. module:: tinycss2

Serialization
=============

In addition to each node’s a :meth:`~tinycss2.ast.Node.serialize` method,
some serialization-related functions are available:

.. autofunction:: serialize
.. autofunction:: serialize_identifier


.. module:: tinycss2.ast

AST nodes
=========

Although you typically don’t need to import it,
the :mod:`tinycss2.ast` module defines a class for every type of node.
(see :ref:`parsing`.)

.. autoclass:: Node()

.. autoclass:: QualifiedRule()
.. autoclass:: AtRule()
.. autoclass:: Declaration()


Component values
----------------

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
========

.. currentmodule:: tinycss2.ast
.. glossary::

    String
        On Python 2.x,
        a byte string (:func:`str <py2:str>`) that only contains ASCII bytes
        or an Unicode string (:func:`unicode <py2:unicode>`).
        On Python 3.x, an Unicode string (:class:`py3:str`).

    Component value
    Component values
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
        or (if requested explicitly) :class:`Comment`
        object.
