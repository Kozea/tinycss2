#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# tinycss2 documentation build configuration file.

import codecs
import re
from os import path


# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx', 'css_diagram_role']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'tinycss2'
copyright = '2013-2017, Simon Sapin'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = re.search("VERSION = '([^']+)'", codecs.open(
    path.join(path.dirname(path.dirname(__file__)), 'tinycss2', '__init__.py'),
    encoding='utf-8',
).read().strip()).group(1)

# The short X.Y version.
version = '.'.join(release.split('.')[:2])

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']

# Output file base name for HTML help builder.
htmlhelp_basename = 'tinycss2doc'

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'tinycss2', 'tinycss2 Documentation',
     ['Simon Sapin'], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'tinycss2', 'tinycss2 Documentation',
   'Simon Sapin', 'tinycss2', 'One line description of project.',
   'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'py2': ('http://docs.python.org/2', None),
    'py3': ('http://docs.python.org/3', None),
    'webencodings': ('http://pythonhosted.org/webencodings/', None)}
