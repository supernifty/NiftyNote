#!/usr/bin/env python

#from distutils.core import setup
from setuptools import setup

setup(
    name='nn',
    version='1.0',
    author='Peter Georgeson',
    author_email='peter@supernifty.org',
    packages=['nn'],
    package_dir={'nn': 'nn'},
    entry_points={
        'console_scripts': ['nn = nn.nn:main']
    },
    url='https://github.com/supernifty/NiftyNote',
    license='LICENSE',
    description=('Manage text notes'),
    long_description=('Manage text notes'),
)
