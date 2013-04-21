import re
from os import path
from setuptools import setup


VERSION = re.search("VERSION = '([^']+)'", open(
    path.join(path.dirname(__file__), 'tinycss2', '__init__.py')
).read().strip()).group(1)


setup(
    name='tinycss2',
    version=VERSION,
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    packages=['tinycss2'],
    install_requires=['webencodings'],
)
