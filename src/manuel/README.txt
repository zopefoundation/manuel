======
Manuel
======

Documentation and testing are important parts of software development.  Often
they can be combined such that you get tests that are well documented or
documentation that is well tested.  That's what Manuel is about.


Overview
========

Manuel parses documents, evaluates their contents, then formats the result of
the evaluation.  All three phases are done in multiple passes.  The passes
continue until the data structure remains unchanged by a pass.

The core functionality is accessed through an instance of a Manuel object.  It
is used to build up our handling of a document type.  Each phase has a
corresponding slot to which various implementations are attached.

    >>> import manuel
    >>> m = manuel.Manuel()
    >>> m
    <manuel.Manuel object at 0x...>


Parsing
-------

Manuel operates on Documents.  Each Document is created from a a string
containing one or more lines.

    >>> source = """\
    ... This is our document, it has several lines.
    ... one: 1, 2, 3
    ... two: 4, 5, 7
    ... three: 3, 5, 1
    ... """
    >>> document = manuel.Document(source)

For example purposes we will create a type of test that consists of a sequence
of numbers so lets create a NumbersTest object to represent the parsed list.

    >>> class NumbersTest(object):
    ...     def __init__(self, description, numbers):
    ...         self.description = description
    ...         self.numbers = numbers

The Document is divided into one or more regions.  Each region is a distinct
"chunk" of the document and will be acted uppon in later (post-parsing) phases.
Initially the Document is made up of a single element, the source string.

    >>> [region.source for region in document]
    ['This is our document, it has several lines.\none: 1, 2, 3\ntwo: 4, 5, 7\nthree: 3, 5, 1\n']

The Document offers a "find_regions" method to assist in locating the portions
of the document a particular parser is interested in.  Given a regular
expression (either as a string, or compiled), it will return "region" objects
that contain the matched source text, the line number (1 based) the region
begins at, as well as the associated re.Match object.

    >>> import re
    >>> numbers_test_finder = re.compile(
    ...     r'^(?P<description>.*?): (?P<numbers>(\d+,?[ ]?)+)$', re.MULTILINE)
    >>> regions = document.find_regions(numbers_test_finder)
    >>> regions
    [<manuel.Region object at 0x...>,
     <manuel.Region object at 0x...>,
     <manuel.Region object at 0x...>]
    >>> regions[0].lineno
    2
    >>> regions[0].source
    'one: 1, 2, 3\n'
    >>> regions[0].start_match.group('description')
    'one'
    >>> regions[0].start_match.group('numbers')
    '1, 2, 3'

If given two regular expressions find_regions will use the first to identify
the begining of a region and the second to identify the end.

    >>> region = document.find_regions(
    ...     re.compile('^one:.*$', re.MULTILINE),
    ...     re.compile('^three:.*$', re.MULTILINE),
    ...     )[0]
    >>> region.lineno
    2
    >>> print region.source
    one: 1, 2, 3
    two: 4, 5, 7
    three: 3, 5, 1

Also, instead of a single "match" attribute, the region will have start_match
and end_match attributes.

    >>> region.start_match
    <_sre.SRE_Match object at 0x...>
    >>> region.end_match
    <_sre.SRE_Match object at 0x...>


Regions must always consist of whole lines.

    >>> document.find_regions('1, 2, 3')
    Traceback (most recent call last):
        ...
    ValueError: Regions must start at the begining of a line.

    >>> document.find_regions('three')
    Traceback (most recent call last):
        ...
    ValueError: Regions must end at the ending of a line.

    >>> document.find_regions(
    ...     re.compile('ne:.*$', re.MULTILINE),
    ...     re.compile('^one:.*$', re.MULTILINE),
    ...     )
    Traceback (most recent call last):
        ...
    ValueError: Regions must start at the begining of a line.

    >>> document.find_regions(
    ...     re.compile('^one:.*$', re.MULTILINE),
    ...     re.compile('^three:', re.MULTILINE),
    ...     )
    Traceback (most recent call last):
        ...
    ValueError: Regions must end at the ending of a line.

Now we can register a parser that will identify the regions we're interested in
and create NumbersTest objects from the source text.

    >>> @m.parser
    ... def parse_numbers_test(document):
    ...     for region in document.find_regions(numbers_test_finder):
    ...         description = region.start_match.group('description')
    ...         numbers = map(
    ...             int, region.start_match.group('numbers').split(','))
    ...         test = NumbersTest(description, numbers)
    ...         document.replace_region(region, test)

    >>> document.parse_with(m)
    >>> [region.source for region in document]
    ['This is our document, it has several lines.\n',
     'one: 1, 2, 3\n',
     'two: 4, 5, 7\n',
     'three: 3, 5, 1\n']
    >>> [region.parsed for region in document]
    [None,
     <NumbersTest object at 0x...>,
     <NumbersTest object at 0x...>,
     <NumbersTest object at 0x...>]


Evaluation
----------

After a document has been parsed the resulting tests are evaluated.  Manuel
provides another method to evaluate tests.  Lets define a function to evaluate
NumberTests.  The function determines whether or not the numbers are in sorted
order and records the result along with the description of the list of numbers.

    >>> class NumbersResult(object):
    ...     def __init__(self, test, passed):
    ...         self.test = test
    ...         self.passed = passed

    >>> @m.evaluater
    ... def evaluate_numbers(document):
    ...     for region in document:
    ...         if not isinstance(region.parsed, NumbersTest):
    ...             continue
    ...         test = region.parsed
    ...         passed = sorted(test.numbers) == test.numbers
    ...         region.evaluated = NumbersResult(test, passed)

    >>> document.evaluate_with(m)
    >>> [region.evaluated for region in document]
    [None,
     <NumbersResult object at 0x...>,
     <NumbersResult object at 0x...>,
     <NumbersResult object at 0x...>]


Formatting
----------

Once the evaluation phase is completed the results are formatted.  You guessed
it: manuel provides a method for formatting results.  We'll build one to format
a message about whether or not our lists of numbers are sorted properly.  A
formatting function returns None when it has no output, or a string otherwise.

    >>> @m.formatter
    ... def format(document):
    ...     for region in document:
    ...         if not isinstance(region.evaluated, NumbersResult):
    ...             continue
    ...         result = region.evaluated
    ...         if not result.passed:
    ...             region.formatted = (
    ...                 "the numbers aren't in sorted order: "
    ...                 + ', '.join(map(str, result.test.numbers)))

Since our test case passed we don't get anything out of the report function.

    >>> document.format_with(m)
    >>> [region.formatted for region in document]
    [None, None, None, "the numbers aren't in sorted order: 3, 5, 1"]


We'll want to use this Manuel object later, so lets stash it away

    >>> sorted_numbers_manuel = m


Doctests
========

We can use manuel to run doctests.  Let's create a simple doctest to
demonstrate with.

    >>> source = """This is my
    ... doctest.
    ...
    ...     >>> 1 + 1
    ...     2
    ... """
    >>> document = manuel.Document(source)

The manuel.doctest module has handlers for the various phases.  First we'll
look at parsing.

    >>> import manuel.doctest
    >>> m = manuel.doctest.Manuel()
    >>> document.parse_with(m)
    >>> for region in document:
    ...     print (region.lineno, region.parsed or region.source)
    (1, 'This is my\ndoctest.\n\n')
    (4, <zope.testing.doctest.Example instance at 0x...>)
    (6, '\n')

Now we can evaluate the examples.

    >>> document.evaluate_with(m)
    >>> for region in document:
    ...     print (region.lineno, region.evaluated or region.source)
    (1, 'This is my\ndoctest.\n\n')
    (4, <manuel.doctest.DocTestResult instance at 0x...>)
    (6, '\n')

And format the results.

    >>> document.format_with(m)
    >>> document.formatted()
    ''

Oh, we didn't have any failing tests, so we got no output.  Let's try again
with a failing test.  This time we'll use the process function to simplify
things.

    >>> document = manuel.Document("""This is my
    ... doctest.
    ...
    ...     >>> 1 + 1
    ...     42
    ... """)

    >>> document.process_with(m)
    >>> print document.formatted()
    File "<memory>", line 4, in <memory>
    Failed example:
        1 + 1
    Expected:
        42
    Got:
        2


Globals
-------

Even though each example is parsed into its own object, state is still shared
between them.

    >>> document = manuel.Document("""
    ...     >>> x = 1
    ...
    ... A little prose to separate the examples.
    ...
    ...     >>> x
    ...     1
    ... """)
    >>> document.process_with(m)
    >>> print document.formatted()

Imported modules are added to the global namespace as well.

    >>> document = manuel.Document("""
    ...     >>> import string
    ...
    ... A little prose to separate the examples.
    ...
    ...     >>> string.digits
    ...     '0123456789'
    ...     
    ... """)
    >>> document.process_with(m)
    >>> print document.formatted()


Combining Test Types
====================

Now that we have both doctests and the silly "sorted numbers" tests, lets
create a single document that has both.

    >>> document = manuel.Document("""
    ... We can test Python...
    ...
    ...     >>> 1 + 1
    ...     42
    ...
    ... ...and lists of numbers.
    ...
    ...     a very nice list: 3, 6, 2
    ... """)

Obviously both of those tests will fail, but first we have to configure Manuel
to understand both test types.  We'll start with a doctest configuration and add
the number list testing on top.

    >>> m = manuel.doctest.Manuel()

Since we already have a Manuel instance configured for our "sorted numbers"
tests, we can extend the built-in doctest configuration with it.

    >>> m.extend(sorted_numbers_manuel)

Now we can process our source that combines both types of tests and see what
we get.

    >>> document.process_with(m)

The document was parsed and has a mixture of prose and parsed doctests and
number tests.

    >>> for region in document:
    ...     print (region.lineno, region.parsed or region.source)
    (1, '\nWe can test Python...\n\n')
    (4, <doctest.Example instance at 0x...>)
    (6, '\n...and lists of numbers.\n\n')
    (9, <NumbersTest object at 0x...>)

We can look at the formatted output to see that each of the two tests failed.

    >>> for region in document:
    ...     if region.formatted:
    ...         print '-'*70
    ...         print region.formatted,
    ----------------------------------------------------------------------
    File "<memory>", line 4, in <memory>
    Failed example:
        1 + 1
    Expected:
        42
    Got:
        2
    ----------------------------------------------------------------------
    the numbers aren't in sorted order:  3, 6, 2


Priorities
==========

Some functionality requires that code be called early or late in a phase.  The
"timing" keyword parameter allows either "early" or "late" to be specified.

Early functions are run first (in arbitrary order), then functions with no
specified timing, then the late functions are called (again in arbitrary
order).  This function also demonstrates the "copy" method of Region objects
and the "insert_region_before" and "insert_region_after" methods of Documents.

    >>> @m.parser(timing='late')
    ... def cloner(document):
    ...     to_be_cloned = None
    ...     # find the region to clone
    ...     document_iter = iter(document)
    ...     for region in document_iter:
    ...         if region.parsed:
    ...             continue
    ...         if region.source.strip().endswith('my clone:'):
    ...             to_be_cloned = document_iter.next().copy()
    ...             break
    ...     # if we found the region to cloned, do so
    ...     if to_be_cloned:
    ...         # make a copy since we'll be mutating the document
    ...         for region in list(document):
    ...             if region.parsed:
    ...                 continue
    ...             if 'clone before *here*' in region.source:
    ...                 clone = to_be_cloned.copy()
    ...                 clone.provenance = 'cloned to go before'
    ...                 document.insert_region_before(region, clone)
    ...             if 'clone after *here*' in region.source:
    ...                 clone = to_be_cloned.copy()
    ...                 clone.provenance = 'cloned to go after'
    ...                 document.insert_region_after(region, clone)

    >>> source = """\
    ... This is my clone:
    ...
    ... clone: 1, 2, 3
    ... 
    ... I want some copies of my clone.
    ... 
    ... For example, I'd like a clone before *here*.
    ...
    ... I'd also like a clone after *here*.
    ... """
    >>> document = manuel.Document(source)
    >>> document.process_with(m)
    >>> [(r.source, r.provenance) for r in document]
    [('This is my clone:\n\n', None),
     ('clone: 1, 2, 3\n', None),
     ('clone: 1, 2, 3\n', 'cloned to go before'),
     ("\nI want some copies of my clone.\n\nFor example, I'd like a clone before *here*.\n\nI'd also like a clone after *here*.\n", None),
     ('clone: 1, 2, 3\n', 'cloned to go after')]
