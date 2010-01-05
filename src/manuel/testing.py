import itertools
import manuel
import os.path
import unittest
import zope.testing.doctest

__all__ = ['TestSuite']

class TestCaseMarker(object):

    def __init__(self, id=''):
        self.id = id


class TestCase(unittest.TestCase):

    def __init__(self, m, regions, globs, setUp=None, tearDown=None):
        unittest.TestCase.__init__(self)
        self.manuel = m
        self.regions = regions
        self.globs = globs
        self.setUp_func = setUp
        self.tearDown_func = tearDown

    def setUp(self):
        if self.setUp_func is not None:
            self.setUp_func(self)

    def tearDown(self):
        if self.tearDown_func is not None:
            self.tearDown_func(self)

    def runTest(self):
        self.regions.evaluate_with(self.manuel, self.globs)
        self.regions.format_with(self.manuel)
        results = [r.formatted for r in self.regions if r.formatted]
        if results:
            DIVIDER = '-'*70 + '\n'
            raise zope.testing.doctest.DocTestFailureException(
                '\n' + DIVIDER + DIVIDER.join(results))

    def debug(self):
        self.setUp()
        self.manuel.debug = True
        self.regions.evaluate_with(self.manuel, self.globs)
        self.tearDown()

    def countTestCases(self):
        return len([r for r in self.regions if r.parsed])

    def id(self):
        return self.regions.id

    def shortDescription(self):
        if self.regions.id:
            return self.regions.location + ':' + self.regions.id
        else:
            return self.regions.location

    __str__ = __repr__ = shortDescription


def group_regions_by_test_case(document):
    """Generate groups of regions according to which testcase they belong"""
    document_iter = iter(document)
    marker = None
    while True:
        accumulated_regions = manuel.RegionContainer()
        while True:
            region = None # being defensive
            try:
                region = document_iter.next()
            except StopIteration:
                if not accumulated_regions:
                    break
            else:
                accumulated_regions.append(region)

                if not isinstance(region.parsed, TestCaseMarker):
                    continue

            # we just found a test case marker or hit the end of the
            # document

            # figure out what this test case's ID is
            accumulated_regions.location = document.location
            if marker is not None and marker.parsed.id:
                accumulated_regions.id = marker.parsed.id

            yield accumulated_regions
            marker = region
            break

        # if there are no more regions, stop
        try:
            region = document_iter.next()
        except StopIteration:
            break

        # put the region we peeked at back so the inner loop can consume it
        document_iter = itertools.chain([region], document_iter)


def TestSuite(m, *paths, **kws):
    """A unittest suite that processes files with Manuel

    The path to each document file is given as a string.

    A number of options may be provided as keyword arguments:

    `setUp`
      A set-up function.  This is called before running the tests in each file.
      The setUp function will be passed a TestCase object.  The setUp function
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
    globs = kws.pop('globs', {})

    # walk up the stack frame to find the module that called this function
    for depth in range(2, 5):
        try:
            calling_module = zope.testing.doctest._normalize_module(
                None, depth=depth)
        except KeyError:
            continue
        else:
            break

    for path in paths:
        if os.path.isabs(path):
            abs_path = os.path.normpath(path)
        else:
            abs_path = os.path.abspath(
                zope.testing.doctest._module_relative_path(
                    calling_module, path))

        document = manuel.Document(
            open(abs_path, 'U').read(), location=abs_path)
        document.parse_with(m)

        for regions in group_regions_by_test_case(document):
            suite.addTest(TestCase(m, regions, globs, **kws))

    return suite
