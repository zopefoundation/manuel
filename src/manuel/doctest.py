from zope.testing import doctest
import StringIO
#import UserDict
import manuel
import os.path


class DocTestResult(StringIO.StringIO):
    pass


class SharedGlobs(dict):

    def copy(self):
        return self


def Manuel(optionflags=0, checker=None):
    m = manuel.Manuel()
    m.runner = doctest.DocTestRunner(optionflags=optionflags, checker=checker)
    m.debug_runner = doctest.DebugRunner(optionflags=optionflags)
    m.globs = SharedGlobs()
    m.debug = False

    @m.parser
    def parse(document):
        for region in list(document):
            if region.parsed:
                continue
            region_start = region.lineno
            region_end = region.lineno + region.source.count('\n')
            for chunk in doctest.DocTestParser().parse(region.source):
                if isinstance(chunk, basestring):
                    continue
                chunk_line_count = (chunk.source.count('\n')
                    + chunk.want.count('\n'))

                split_line_1 = region_start + chunk.lineno
                split_line_2 = split_line_1 + chunk_line_count

                # if there is some source we need to trim off the front...
                if split_line_1 > region.lineno:
                    _, region = document.split_region(region, split_line_1)

                if split_line_2 <= region_end:
                    found, region = document.split_region(region, split_line_2)
                    document.replace_region(found, chunk)

                assert region in document

    @m.evaluater
    def evaluate(document):
        for region in document:
            if not isinstance(region.parsed, doctest.Example):
                continue
            result = DocTestResult()
            test_name = os.path.split(document.location)[1]
            if m.debug:
                runner = m.debug_runner
            else:
                runner = m.runner

            runner.DIVIDER = '' # disable unwanted result formatting
            runner.run(
                doctest.DocTest([region.parsed], m.globs, test_name,
                    document.location, 0, None),
                out=result.write, clear_globs=False)
            region.evaluated = result

    @m.formatter
    def format(document):
        for region in document:
            if not isinstance(region.evaluated, DocTestResult):
                continue
            region.formatted = region.evaluated.getvalue().lstrip()

    return m
