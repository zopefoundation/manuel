from zope.testing import renormalizing
import manuel
import manuel.codeblock
import manuel.doctest
import manuel.testing
import re
import unittest

#doctest = manuel.absolute_import('doctest')
from zope.testing import doctest

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])
    suite = unittest.TestSuite()

    tests = ['README.txt', 'footnote.txt', 'bugs.txt', 'code-block.txt',
        'isolation.txt', 'table-example.txt']

    # run the tests with Manuel's doctest support
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    # add in the codeblock extension
    m.extend(manuel.codeblock.Manuel())
    # build the test suite
    suite.addTest(manuel.testing.TestSuite(m, *tests))

    return suite
