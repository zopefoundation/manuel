from setuptools import setup, find_packages
import os
import sys

long_description = (
    open('README.txt').read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

if sys.version > '3':
    extras = dict(
    dependency_links = ['.'],
    use_2to3 = True,
    convert_2to3_doctests = ['src/manuel/README.txt',
                             'src/manuel/table-example.txt',
                             'src/manuel/bugs.txt',
                             'src/manuel/capture.txt',
                             ],)
else:
    extras = {}


setup(
    name='manuel',
    version='0',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description= 'Manuel lets you build tested documentation.',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    long_description = long_description,
    test_suite = 'manuel.tests.test_suite',
    **extras
    )
