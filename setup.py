import os

from setuptools import setup, find_packages

long_description = (
    open(os.path.join('src', 'manuel', 'README.txt')).read()
    + '\n\n'
    + open(os.path.join('src', 'manuel', 'table-example.txt')).read()
    + '\n\n'
    + open('CHANGES.txt').read()
    )

setup(
    name='manuel',
    version='1.0.0a7',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description=
        'Manuel lets you combine traditional doctests with new test syntax '
        'that you build yourself or is inlcuded in Manuel.',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    long_description = long_description,
    )
