from setuptools import setup, find_packages
import os

long_description = (
    open('README.txt').read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

setup(
    name='manuel',
    version='1.1.0',
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
        'zope.testing >= 3.9.1',
        ],
    include_package_data=True,
    long_description = long_description,
    )
