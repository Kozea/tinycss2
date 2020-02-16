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

.. _virtual environment: https://packaging.python.org/tutorials/installing-packages/#creating-virtual-environments
.. _pip: http://pip-installer.org/
.. _webencodings: http://pythonhosted.org/webencodings/


Parsing CSS
-----------

tinycss2’s main goal is to parse CSS into Python objects. Parsing CSS is done
using the :func:`~tinycss2.parse_stylesheet` function.

.. code-block:: python

   import tinycss2

   rules = tinycss2.parse_stylesheet('body div { width: 50% }')

   print(rules)
   # [<QualifiedRule … { … }>]
   rule = rules[0]

   print(rule.prelude)
   # [
   #     <IdentToken body>,
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


Serializing CSS
---------------

tinycss2 is also able to generate CSS strings out of abstact Python trees.

.. code-block:: python

   import tinycss2

   rules = tinycss2.parse_stylesheet('body div { width: 50% }')
   rule = rules[0]

   print(rule.serialize())
   # 'body div { width: 50% }'

