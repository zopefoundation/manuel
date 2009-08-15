from zope.testing import renormalizing
import manuel
import manuel.capture
import manuel.codeblock
import manuel.doctest
import manuel.ignore
import manuel.testcase
import manuel.testing
import os.path
import re
import unittest

#doctest = manuel.absolute_import('doctest')
from zope.testing import doctest


def get_abs_path(p):
    def fake():
        pass
    # this contorted dance is neccesitated by me wanting to be able to run the
    # tests with "bin/py src/manuel/tests.py" since bin/py uses execfile, which
    # means that __file__ -- which I'd normally use here -- will be "bin/py"
    # not the path to *this* module
    here = os.path.dirname(fake.func_code.co_filename)
    return os.path.join(os.getcwd(), here, p)


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])

    tests = ['../index.txt', 'table-example.txt', 'README.txt', 'bugs.txt',
        'capture.txt']

    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m += manuel.codeblock.Manuel()
    m += manuel.capture.Manuel()
    return manuel.testing.TestSuite(m, *tests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
