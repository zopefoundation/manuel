import os

from setuptools import setup, find_packages

setup(
    name='manuel',
    version='1.0.0a3',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description=
        'Documentation and testing are important parts of software '
        'development.  Often they can be combined such that you get tests '
        'that are well documented or documentation that is well tested.  '
        'That\'s what Manuel is about.',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    long_description = (
        open(os.path.join('src', 'manuel', 'README.txt')).read()
        + '\n\n'
        + open('CHANGES.txt').read()
        )
    )
