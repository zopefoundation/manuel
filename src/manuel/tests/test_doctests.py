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

_NO_ROLES = """\
Stuff

.. code-block:: python

   def foo(abc):
       return 1

More stuff
"""

_WITH_ROLES = """\
Stuff

.. code-block:: python

   def foo(abc):
       return 1

More stuff.
"""

class Test_find_code_blocks(unittest.TestCase):
    def _callFUT(self, document):
        from manuel.codeblock import find_code_blocks
        return find_code_blocks(document)

    def test_start_end_no_roles(self):
        region = Region(_NO_ROLES)
        document = DummyDocument([region])
        self._callFUT(document)

class Region(object):
    lineno = 1
    def __init__(self, source):
        self.source = source

class DummyDocument(object):
    def __init__(self, regions):
        self._regions = regions
        self.claimed = []

    def find_regions(self, start, end):
        return self._regions

    def claim_region(self, region):
        self.claimed.append(region)
    
def test_suite():
    optionflags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    checker = renormalizing.RENormalizing([
        (re.compile(r'<zope\.testing\.doctest\.'), '<doctest.'),
        ])

    tests = ['../../index.txt', '../table-example.txt', '../README.txt',
             '../bugs.txt', '../capture.txt']

    m = manuel.ignore.Manuel()
    m += manuel.doctest.Manuel(optionflags=optionflags, checker=checker)
    m += manuel.codeblock.Manuel()
    m += manuel.capture.Manuel()
    return manuel.testing.TestSuite(m, *tests)


if __name__ == '__main__':
    unittest.TextTestRunner().run(test_suite())
