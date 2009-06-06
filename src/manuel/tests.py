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

    tests = ['README.txt', 'footnote.txt', 'bugs.txt']

    # Run the tests once with doctest.
    suite.addTest(
        doctest.DocFileSuite(optionflags=optionflags, checker=checker, *tests))

    # Run them again with Manuel's doctest support.
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    suite.addTest(manuel.testing.TestSuite(m, *tests))

    # Run the table example with doctest plus the codeblock extension.
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m.extend(manuel.codeblock.Manuel())
    suite.addTest(manuel.testing.TestSuite(m, 'table-example.txt'))
    return suite
