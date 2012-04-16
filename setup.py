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

tests_require = ['zope.testing']

setup(
    name='manuel',
    version='0',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description='Manuel lets you build tested documentation.',
    classifiers=[
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 3',
        ],
    license='ZPL',
    extras_require={
        'tests': tests_require,
        },
    tests_require = tests_require,
    test_suite = 'manuel.tests.test_suite',
    install_requires=[
        'setuptools',
        'six',
        ],
    include_package_data=True,
    long_description = long_description,
    )
