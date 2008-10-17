from zope.testing import doctest
from zope.testing import renormalizing
import manuel
import manuel.doctest
import manuel.testing
import re
import unittest

#doctest = manuel.absolute_import('doctest')

def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])
    suite = unittest.TestSuite()

    tests = ['README.txt', 'footnote.txt']

    # Run the tests once with just doctest.
    README = doctest.DocFileSuite(*tests, **{
        'optionflags': optionflags,
        'checker': checker})
    suite.addTest(README)

    # Run them again with manuel.
    m = manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    suite.addTest(manuel.testing.TestSuite(m, *tests))

    return suite
