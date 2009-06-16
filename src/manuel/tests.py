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

def run_tests():
    unittest.TextTestRunner().run(test_suite())

if __name__ == '__main__':
    run_tests()
