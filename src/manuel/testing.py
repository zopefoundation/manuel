from zope.testing import doctest
import manuel
import unittest


__all__ = ['TestSuite']

class TestCase(unittest.TestCase):
    def __init__(self, m, document, setUp=None, tearDown=None,
            globs=None):
        unittest.TestCase.__init__(self)
        self.manuel = m
        self.document = document
        self.setUp_func = setUp
        self.tearDown_func = tearDown
        self.globs = globs

        # we want to go ahead and do the parse phase so the countTestCases
        # method can get a good idea of how many tests there are
        document.parse_with(m)

    def setUp(self):
        if self.setUp_func is not None:
            self.setUp_func(self.manuel)

    def tearDown(self):
        if self.tearDown_func is not None:
            self.tearDown_func(self.manuel)

    def runTest(self):
        self.document.evaluate_with(self.manuel)
        self.document.format_with(self.manuel)
        results = [r.formatted for r in self.document if r.formatted]
        if results:
            DIVIDER = '-'*70 + '\n'
            raise self.failureException(
                '\n' + DIVIDER + DIVIDER.join(results))

    def debug(self):
        self.setUp()
        self.manuel.debug = True
        self.document.evaluate_with(self.manuel)
        self.tearDown()

    def countTestCases(self):
        return len([r for r in self.document if r.parsed])

    def id(self):
        return self.document.location

    def shortDescription(self):
        return "Manuel Test: " + self.document.location

    __str__ = __repr__ = shortDescription


def TestSuite(m, *paths, **kws):
    """A unittest suite that processes files with Manuel

    The path to each document file is given as a string.

    A number of options may be provided as keyword arguments:

    `setUp`
      A set-up function.  This is called before running the tests in each file.
      The setUp function will be passed a Manuel object.  The setUp function
      can access the test globals as the `globs` attribute of the instance
      passed.

    `tearDown`
      A tear-down function.  This is called after running the tests in each
      file.  The tearDown function will be passed a Manuel object.  The
      tearDown function can access the test globals as the `globs` attribute of
      the instance passed.

    `globs`
      A dictionary containing initial global variables for the tests.
    """

    suite = unittest.TestSuite()

    # inspect the stack frame to find the module that called this function
    calling_module = doctest._normalize_module(None, depth=2)

    for path in paths:
        abs_path = doctest._module_relative_path(calling_module, path)
        document = manuel.Document(open(abs_path).read(), location=abs_path)
        suite.addTest(TestCase(m, document, **kws))

    return suite
