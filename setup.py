#!/usr/bin/env python

import setuptools
import pathlib

name = "nn"
version = "0.1"
release = "0.1.0"
here = pathlib.Path(__file__).parent.resolve()

setuptools.setup(
    name=name,
    version=version,
    author='Peter Georgeson',
    author_email='peter@supernifty.org',
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            'dotplot = nn.nn:main',
        ],
    },
    url='https://github.com/supernifty/NiftyNote',
    description=('Manage text notes'),
    long_description=('Manage text notes'),
    license="LICENSE"
)
