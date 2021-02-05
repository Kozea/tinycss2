Contribute
==========

You want to add some code to tinycss2, launch its tests or improve its
documentation? Thank you very much! Here are some tips to help you play with
tinycss2 in good conditions.

The first step is to clone the repository, create a virtual environment and
install tinycss2 dependencies.

.. code-block:: shell

   git clone https://github.com/Kozea/tinycss2.git
   cd tinycss2
   python -m venv venv
   venv/bin/pip install .[doc,test]

You can then let your terminal in the current directory and launch Python to
test your changes. ``import tinycss2`` will then import the working directory
code, so that you can modify it and test your changes.

.. code-block:: shell

   venv/bin/python


Code & Issues
-------------

If you’ve found a bug in tinycss2, it’s time to report it, and to fix it if you
can!

You can report bugs and feature requests on GitHub_. If you want to add or
fix some code, please fork the repository and create a pull request, we’ll be
happy to review your work.

.. _GitHub: https://github.com/Kozea/tinycss2


Tests
-----

Tests are stored in the ``tests`` folder at the top of the repository. They use
the pytest_ library.

You can launch tests (with code coverage and lint) using the following command::

  venv/bin/python -m pytest

.. _pytest: https://docs.pytest.org/


Documentation
-------------

Documentation is stored in the ``docs`` folder at the top of the repository. It
relies on the Sphinx_ library.

You can build the documentation using the following command::

  venv/bin/sphinx-build docs docs/_build

The documentation home page can now be found in the
``/path/to/tinycss2/docs/_build/index.html`` file. You can open this file in a
browser to see the final rendering.

.. _Sphinx: https://www.sphinx-doc.org/
