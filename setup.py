#!/usr/bin/python

import os
import setuptools


here = os.path.abspath(os.path.dirname(__file__))

try:
    README = open(os.path.join(here, 'README')).read()
except:
    README = ''


setuptools.setup(
    name = 'py3oserror',
    version = '0.1',
    license = 'BSD',
    description = "Python 3.3's OSError subclasses for Python 2",
    long_description = README,
    author = 'Matt Good',
    author_email = 'matt@matt-good.net',
    url = 'http://github.com/mgood/py3oserror/',
    platforms = 'any',

    py_modules = ['py3oserror'],

    zip_safe = True,
    verbose = False,
)
