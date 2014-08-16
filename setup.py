import re
import codecs
from os import path
from setuptools import setup


VERSION = re.search("VERSION = '([^']+)'", codecs.open(
    path.join(path.dirname(__file__), 'tinycss2', '__init__.py'),
    encoding="utf-8",
).read().strip()).group(1)

README = codecs.open(
    path.join(path.dirname(__file__), 'README.rst'),
    encoding="utf-8",
).read()

setup(
    name='tinycss2',
    version=VERSION,
    description='Modern CSS parser for Python',
    long_description=README,
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    packages=['tinycss2'],
    install_requires=['webencodings>=0.4'],
    package_data={'tinycss2': ['css-parsing-tests/*']},
)
