Changelog
=========


Version 1.4.0
-------------

Released on 2024-10-24

* Support CSS Color Level 4


Version 1.3.0
-------------

Released on 2024-04-23.

* Support CSS nesting
* Deprecate parse_declaration_list, use parse_blocks_contents instead


Version 1.2.1
-------------

Released on 2022-10-18.

* Fix tests included in the source tarball


Version 1.2.0
-------------

Released on 2022-10-17.

* Drop support of Python 3.6
* Fix serialization of nested functions with no parameters
* Don’t use pytest plugins by default


Version 1.1.1
-------------

Released on 2021-11-22.

* Add support of Python 3.10.
* Include tests in source package.


Version 1.1.0
-------------

Released on 2020-10-29.

* Drop support of Python 3.5, add support of Python 3.9.
* Fix ResourceWarning in tests.
* Use Python standard library’s HSL to RGB converter.
* Use GitHub Actions for tests.
* New code structure, new packaging, new documentation.


Version 1.0.2
-------------

Released on 2019-03-21.

* Don't crash when indent tokens have no lowercase equivalent name.


Version 1.0.1
-------------

Released on 2019-03-06.

* Fix tests launched by CI.
* Parse "--" ident tokens correctly.


Version 1.0.0
-------------

Released on 2019-03-04.

* Drop Python 2.7, 3.3 and 3.4 support.
* Allow leading double dash syntax for ident tokens, allowing CSS variables to
  be parsed correctly.
* Test with PyPy3.
* Force tests to parse JSON files as UTF-8.
* Clean packaging.


Version 0.6.1
-------------

Released on 2017-10-02.

* Update documentation.


Version 0.6.0
-------------

Released on 2017-08-16.

* Don't allow identifiers starting with two dashes.
* Don't use Tox for tests.
* Follow semantic versioning.


Version 0.5
-----------

Released on 2014-08-19.

* Update for spec changes.
* Add a :attr:`tinycss2.ast.WhitespaceToken.value` attribute
  to :class:`tinycss2.ast.WhitespaceToken`.
* **Breaking change**: CSS comments are now preserved
  as :class:`tinycss2.ast.Comment` objects by default.
  Pass ``skip_comments=True`` to parsing functions to get the old behavior.
* **Breaking change**: Top-level comments and whitespace are now preserved
  when parsing a stylesheet, rule list, or declaration list.
  Pass ``skip_comments=True`` and ``skip_whitespace=True``
  to get the old behavior.
* Test on Python 3.4 and PyPy3.
* Set up continous integration on Travis-CI.


Version 0.4
-----------

Released on 2014-01-04.

* Fix :class:`tinycss2.ast.HashToken` starting with a non-ASCII character.
* Fix :func:`repr` on AST nodes.


Version 0.3
-----------

Released on 2013-12-27.

* Document all the things!
* Add serialization.
* Merge ``tinycss2.color3.parse_color_string`` behavior into
  :func:`tinycss2.color3.parse_color`.
* Fix and test parsing form bytes and tokenization of <unicode-range>.


Version 0.2
-----------

Released on 2013-09-02.

* Add parsing for <An+B>, as in ``:nth-child()`` and related Selectors
  pseudo-classes.


Version 0.1
-----------

Released on 2013-08-31.

First PyPI release. Contains:

* Decoding from bytes using ``@charset``.
* Tokenization.
* Parsing for "generic" rules and declarations.
* Parsing for CSS Color Level 3.
* Tests for all of the above, except for decoding from bytes.
