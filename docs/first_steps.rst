First Steps
===========


Installation
------------

The easiest way to use tinycss2 is to install it in a Python `virtual
environment`_. When your virtual environment is activated, you can then install
tinycss2 with pip_::

    pip install tinycss2

This will also automatically install tinycss2’s only dependency, webencodings_.
tinycss2 and webencodings both only contain Python code and should work on any
Python implementation.

tinycss2 also is packaged for many Linux distributions (Debian, Ubuntu, Fedora,
Archlinux, Gentoo…).

.. _virtual environment: https://packaging.python.org/guides/installing-using-pip-and-virtual-environments/
.. _pip: https://pip.pypa.io/
.. _webencodings: https://pythonhosted.org/webencodings/


CSS Parsing
-----------

tinycss2’s main goal is to parse CSS and return corresponding Python
objects. Parsing CSS is done using the :func:`~tinycss2.parse_stylesheet`
function.

.. code-block:: python

   import tinycss2

   rules = tinycss2.parse_stylesheet('#cell div { width: 50% }')

   print(rules)
   # [<QualifiedRule … { … }>]
   rule = rules[0]

   print(rule.prelude)
   # [
   #     <HashToken #cell>,
   #     <WhitespaceToken>,
   #     <IdentToken div>,
   #     <WhitespaceToken>,
   # ]

   print(rule.content)
   # [
   #     <WhitespaceToken>,
   #     <IdentToken width>,
   #     <LiteralToken :>,
   #     <WhitespaceToken>,
   #     <PercentageToken 50%>,
   #     <WhitespaceToken>,
   # ]

In this example, you can see that ``'body div { width: 50% }'`` is a list of
one CSS `qualified rule`_. This rule contains a prelude (a CSS selector) and
some content (one CSS property with its value).

The prelude contains 4 parts, called tokens_:

- a hash token (``#cell``),
- a whitespace token (between ``#cell`` and ``div``),
- an identifier token (``div``),
- a whitespace token (after ``div``).

The content, that is between ``{`` and ``}``, contains 6 tokens:

- a whitespace token (before ``width``),
- an identifier token (``width``),
- a literal token (``:``),
- a whitespace token (between ``:`` and ``50%``),
- a percentage token (``50%``),
- a whitespace token (after ``50%``).

You can find what you can do with this rule and these tokens on the
:ref:`Common Use Cases` page.

.. _qualified rule: https://www.w3.org/TR/css-syntax-3/#qualified-rule
.. _tokens: https://www.w3.org/TR/css-syntax-3/#tokenization
