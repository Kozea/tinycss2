# tinycss2 documentation build configuration file.

import sys
from pathlib import Path

import tinycss2

# Add current path for css_diagram_role
sys.path.append(str(Path(__file__).parent))

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom ones.
extensions = [
    'sphinx.ext.autodoc', 'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel', 'css_diagram_role']

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix of source filenames.
source_suffix = '.rst'

# The master toctree document.
master_doc = 'index'

# General information about the project.
project = 'tinycss2'
copyright = 'Simon Sapin and contributors'

# The version info for the project you're documenting, acts as replacement for
# |version| and |release|, also used in various other places throughout the
# built documents.
#
# The full version, including alpha/beta/rc tags.
release = tinycss2.__version__

# The short X.Y version.
version = '.'.join(release.split('.')[:2])

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
exclude_patterns = ['_build']

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'monokai'

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

html_theme_options = {
    'top_of_page_buttons': ['edit'],
    'source_edit_link':
    'https://github.com/CourtBouillon/pydyf/edit/main/docs/{filename}',
}

# Favicon URL
html_favicon = 'https://www.courtbouillon.org/static/images/favicon.png'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = []

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'https://www.courtbouillon.org/static/docs-furo.css',
]

# Output file base name for HTML help builder.
htmlhelp_basename = 'tinycss2doc'

# One entry per manual page. List of tuples
# (source start file, name, description, authors, manual section).
man_pages = [
    ('index', 'tinycss2', 'tinycss2 Documentation',
     ['Simon Sapin and contributors'], 1)
]

# Grouping the document tree into Texinfo files. List of tuples
# (source start file, target name, title, author,
#  dir menu entry, description, category)
texinfo_documents = [
  ('index', 'tinycss2', 'tinycss2 Documentation',
   'Simon Sapin', 'tinycss2',
   'A low-level CSS parser and generator written in Python.',
   'Miscellaneous'),
]

# Example configuration for intersphinx: refer to the Python standard library.
intersphinx_mapping = {
    'python': ('https://docs.python.org/3/', None),
    'webencodings': ('https://pythonhosted.org/webencodings/', None),
}
