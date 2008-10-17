import os

from setuptools import setup, find_packages

setup(
    name='manuel',
    version='1.0.0a2',
    url = 'http://pypi.python.org/pypi/manuel',
    packages=find_packages('src'),
    package_dir={'':'src'},
    zip_safe=False,
    author='Benji York',
    author_email='benji@benjiyork.com',
    description='Design test syntax to match the task at hand and/or make '
        'documentation testable.',
    license='ZPL',
    install_requires=[
        'setuptools',
        'zope.testing',
        ],
    include_package_data=True,
    )
