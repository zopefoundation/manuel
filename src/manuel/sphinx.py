import os
import re
import manuel
import textwrap
doctest = __import__('doctest')
import manuel.doctest

BLOCK_START = re.compile(r'^\.\. test(setup|code|output):: *(testgroup)?', re.MULTILINE)
BLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')

# TODO: We need to handle groups, which we don't, and we need to handle that
# for doctests as well, which we don't, and we probably need to handle
# doctest options as well. And we might want to make sure that we are compatible
# with how sphinx handles different cases, like groups and the '*' group and
# setup and globals, etc.

class TestSetup(object):
    def __init__(self, code, group):
        self.code = code
        self.group = group

class TestCode(object):
    def __init__(self, code, group):
        self.code = code
        self.group = group

class TestOutput(object):
    def __init__(self, code, group):
        self.code = code
        self.group = group

class TestCase(object):
    def __init__(self, setup, code, output):
        if setup:
            self.code = setup.code + '\n' + code.code
        else:
            self.code = code.code
        self.output = output.code
        # When we start handling groups, we want to get the group of the
        # test here, so we can put that in the test report, I think:
        self.group = ''
        
def parse(document):
    groups = {}
    previous_type = ''
    for region in document.find_regions(BLOCK_START, BLOCK_END):
        source = textwrap.dedent('\n'.join(region.source.splitlines()[1:]))
        document.claim_region(region)
        type_, group = region.start_match.groups()
        if type_ == 'setup':
            region.parsed = TestSetup(source, region.start_match.groups()[1])
        elif type_ == 'code':
            region.parsed = TestCode(source, region.start_match.groups()[1])
        elif type_ == 'output':
            region.parsed = TestOutput(source, region.start_match.groups()[1])
    
    # Now go through the document and make all groups of regions into testcases.
    #iterator = iter(document)
    setup_region = None
    code_region = None
    for region in document:
        if isinstance(region.parsed, TestSetup):
            # This is a new block, finish the old:
            if code_region:
                code_region.parsed = TestCase(setup_region.parsed,
                                              code_region.parsed,
                                              None)
                code_region = None
            setup_region = region
        elif isinstance(region.parsed, TestCode):
            if code_region:
                # This is a new block, yield the old:
                code_region.parsed = TestCase(setup_region.parsed,
                                              code_region.parsed,
                                              None)
                setup_region = None
            code_region = region
        elif isinstance(region.parsed, TestOutput):
            # This is the end of a block
            code_region.parsed = TestCase(setup_region.parsed,
                                          code_region.parsed,
                                          region.parsed)
            setup_region, code_region = None, None

def monkey_compile(code, name, type, flags, dont_inherit):
    return compile(code, name, 'exec', flags, dont_inherit)
doctest.compile = monkey_compile

def evaluate(region, document, globs):
    if not isinstance(region.parsed, TestCase):
        return

    result = manuel.doctest.DocTestResult()
    if region.parsed.group:
        test_name = region.parsed.group
    else:
        test_name = os.path.split(document.location)[1]
    
    exc_msg = None
    output = region.parsed.output
    if output:
        match = doctest.DocTestParser._EXCEPTION_RE.match(output)
        if match:
            exc_msg = match.group('msg')
            
    example = doctest.Example(region.parsed.code, output, exc_msg=exc_msg,
                              lineno=region.lineno)
    test = doctest.DocTest([example], globs, test_name, document.location,
                           region.lineno-1, None)
    runner = doctest.DocTestRunner()
    runner.DIVIDER = '' # disable unwanted result formatting
    runner.run(test, clear_globs=False)
    region.evaluated = result
    

class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [parse], [evaluate])
