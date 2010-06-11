##############################################################################
#
# Copyright (c) 2004-2007 Zope Foundation and Contributors.
# All Rights Reserved.
#
# This software is subject to the provisions of the Zope Public License,
# Version 2.1 (ZPL).  A copy of the ZPL should accompany this distribution.
# THIS SOFTWARE IS PROVIDED "AS IS" AND ANY AND ALL EXPRESS OR IMPLIED
# WARRANTIES ARE DISCLAIMED, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF TITLE, MERCHANTABILITY, AGAINST INFRINGEMENT, AND FITNESS
# FOR A PARTICULAR PURPOSE.
#
##############################################################################
"""Setup for manuel package
"""
from setuptools import setup, find_packages

long_description = (
    open('README.txt').read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

setup(
    name='manuel',
    version='1.2.0',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description= 'Manuel lets you build tested documentation.',
    license='ZPL',
    extras_require={
        'tests': ['zope.testing']
        },
    install_requires=[
        'setuptools',
        'zope.testrunner',
        ],
    include_package_data=True,
    long_description = long_description,
    )
