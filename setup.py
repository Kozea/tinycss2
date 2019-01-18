#!/usr/bin/env python
# coding: utf8

import codecs
import os.path
import re
import sys

from setuptools import setup


VERSION = re.search("VERSION = '([^']+)'", codecs.open(
    os.path.join(os.path.dirname(__file__), 'tinycss2', '__init__.py'),
    encoding='utf-8',
).read().strip()).group(1)

README = codecs.open(
    os.path.join(os.path.dirname(__file__), 'README.rst'),
    encoding='utf-8',
).read()

needs_pytest = {'pytest', 'test', 'ptr'}.intersection(sys.argv)
pytest_runner = ['pytest-runner'] if needs_pytest else []

setup(
    name='tinycss2',
    version=VERSION,
    description='Low-level CSS parser for Python',
    long_description=README,
    license='BSD',
    author='Simon Sapin',
    author_email='simon.sapin@exyr.org',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Topic :: Text Processing',
    ],
    packages=['tinycss2'],
    install_requires=['webencodings>=0.4'],
    package_data={'tinycss2': ['css-parsing-tests/*']},
    setup_requires=pytest_runner,
    test_suite='tinycss2.test',
    tests_require=[
        'pytest-runner', 'pytest-cov', 'pytest-flake8', 'pytest-isort'],
    extras_require={'test': [
        'pytest-runner', 'pytest-cov', 'pytest-flake8', 'pytest-isort']},
)
