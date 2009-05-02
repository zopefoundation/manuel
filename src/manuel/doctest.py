import StringIO
import manuel
import os.path

doctest = manuel.absolute_import('doctest')
#from zope.testing import doctest

class DocTestResult(StringIO.StringIO):
    pass


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


def evaluate(m, region, document, globs):
    if not isinstance(region.parsed, doctest.Example):
        return
    result = DocTestResult()
    test_name = os.path.split(document.location)[1]
    if m.debug:
        runner = m.debug_runner
    else:
        runner = m.runner

    runner.DIVIDER = '' # disable unwanted result formatting
    runner.run(
        doctest.DocTest([region.parsed], globs, test_name,
            document.location, 0, None),
        out=result.write, clear_globs=False)
    region.evaluated = result


def format(document):
    for region in document:
        if not isinstance(region.evaluated, DocTestResult):
            continue
        region.formatted = region.evaluated.getvalue().lstrip()


class Manuel(manuel.Manuel):

    def __init__(self, optionflags=0, checker=None):
        self.runner = doctest.DocTestRunner(optionflags=optionflags,
            checker=checker)
        self.debug_runner = doctest.DebugRunner(optionflags=optionflags)
        self.debug = False
        def evaluate_closure(region, document, globs):
            # capture "self"
            evaluate(self, region, document, globs)
        manuel.Manuel.__init__(self, [parse], [evaluate_closure], [format])
