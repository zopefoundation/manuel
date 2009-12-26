import unittest

_NO_ROLES = """\
.. code-block:: python

   def foo(abc):
       return 1
"""

_WITH_ROLES = """\
.. code-block:: python
   :linenos:
   :other:

   def foo(abc):
       return 1
"""

class Test_find_code_blocks(unittest.TestCase):
    def _callFUT(self, document):
        from manuel.codeblock import find_code_blocks
        return find_code_blocks(document)

    def test_start_end_no_roles(self):
        region = DummyRegion(_NO_ROLES)
        document = DummyDocument([region])
        self._callFUT(document)
        self.assertEqual(document.claimed, [region])
        self.assertEqual(region.parsed.code.co_names, ('foo',))

    def test_start_end_with_roles(self):
        region = DummyRegion(_WITH_ROLES)
        document = DummyDocument([region])
        self._callFUT(document)
        self.assertEqual(document.claimed, [region])
        self.assertEqual(region.parsed.code.co_names, ('foo',))

    def test_start_end_multiple_regions(self):
        region1 = DummyRegion(_WITH_ROLES)
        region2 = DummyRegion(_NO_ROLES)
        document = DummyDocument([region1, region2])
        self._callFUT(document)
        self.assertEqual(document.claimed, [region1, region2])
        self.assertEqual(region1.parsed.code.co_names, ('foo',))
        self.assertEqual(region2.parsed.code.co_names, ('foo',))

class DummyRegion(object):
    lineno = 1
    def __init__(self, source):
        self.source = source

class DummyDocument(object):
    location = 0
    def __init__(self, regions):
        self._regions = regions
        self.claimed = []

    def find_regions(self, start, end):
        return self._regions

    def claim_region(self, region):
        self.claimed.append(region)
    
def test_suite():
    suite = unittest.TestSuite()
    suite.addTest(unittest.makeSuite(Test_find_code_blocks))
    return suite

if __name__ == '__main__':
    unittest.main()
