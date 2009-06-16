from zope.testing import renormalizing
import manuel
import manuel.codeblock
import manuel.doctest
import manuel.testing
import os.path
import re
import unittest

#doctest = manuel.absolute_import('doctest')
from zope.testing import doctest


def get_abs_path(p):
    def fake():
        pass
    here = os.path.dirname(fake.func_code.co_filename)
    return os.path.join(os.getcwd(), here, p)


def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])
    suite = unittest.TestSuite()

    tests = ['README.txt', 'footnote.txt', 'bugs.txt', 'codeblock.txt',
        'isolation.txt', 'table-example.txt']

    tests = map(get_abs_path, tests)

    # run the tests with Manuel's doctest support
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    # add in the codeblock extension
    m.extend(manuel.codeblock.Manuel())
    # build the test suite
    suite.addTest(manuel.testing.TestSuite(m, *tests))

    return suite

test_suite.__test__ = False # tell nose not to treat this as a test case

if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
