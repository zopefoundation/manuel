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

doctest = manuel.absolute_import('doctest')

here = os.path.dirname(os.path.abspath(__file__))

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
    return manuel.testing.TestSuite(m, *tests,
        globs={'path_to_test': os.path.join(here, 'bugs.txt')})


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
