Going Further
=============


Why tinycss2?
-------------

tinycss2 is the rewrite of tinycss_ with a simpler API, based on the more
recent `CSS Syntax Level 3 specification`_. tinycss has itself been created to
replace `cssutils <https://cthedot.de/cssutils/>`_.

Its main purpose is to be WeasyPrint_’s CSS parser, but it’s been used by many
other projects, including Reddit_.

WeasyPrint’s first CSS parser was cssutils. Even if it has been really useful,
it was really limited to CSS 2.1 and needed a lot of work to include CSS 3
features such as ``@page``. That’s why `Simon Sapin decided to write tinycss`_.

tinycss was simple and fast, but it was really bound to specificities included
in various modules. For example, dedicated Python modules were needed to
support *Paged Media Level 3* or *Fonts Level 3* specifications.

This situation was not sustainable because it required changes in tinycss each
time a new CSS syntax was added. Moreover, *CSS Syntax Level 3* had been
released, defining a low-level grammar used by all the other CSS modules.

tinycss2 has been created as a *low-level* parser, as it doesn’t parse all of
CSS: it doesn’t know about the syntax of any specific properties or
at-rules. Instead, it provides a set of functions that can be composed to
support exactly the parts of CSS you’re interested in, including new or
non-standard rules or properties, without modifying tinycss2 or having a
complex hook or plugin system.

.. _tinycss: https://pythonhosted.org/tinycss/
.. _CSS Syntax Level 3 specification: https://www.w3.org/TR/css-syntax-3/
.. _WeasyPrint: https://weasyprint.org/
.. _Reddit: https://www.reddit.com/r/cssnews/comments/24anzb/css_change_the_filter_has_been_rewritten/
.. _Simon Sapin decided to write tinycss: https://exyr.org/2012/tinycss-css-parser/


Why Python?
-----------

Python is a really good language to design a small, OS-agnostic parser. As it
is object-oriented, it gives the possibility to follow the specification with
high-level classes and a small amount of very simple code.

And of course, WeasyPrint is written in Python too, giving an obvious reason
for this choice.

Speed is not tinycss2’s main goal. Parsing CSS is a very small part of web
rendering, that’s why improving tinycss2’s performance is not helpful to get
fast document generation. Code simplicity, maintainability and flexibility are
more important goals for this library, as they give the ability to stay really
close to the specification and to fix bugs easily.
