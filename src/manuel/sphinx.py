import os
import re
import manuel
import textwrap
doctest = __import__('doctest')
import manuel.doctest

BLOCK_START = re.compile(r'^\.\. test(setup|code|output)::(.*?)\n\s*\n',
                         re.MULTILINE|re.DOTALL)
BLOCK_END = re.compile(r'(\n\Z|\n(?=\S))')

# TODO: We need to handle groups, which we don't, and we need to handle that
# for doctests as well, which we don't. And we might want to make sure that we
# are compatible with how sphinx handles different cases, like groups and the
# '*' group and setup and globals, etc.

class TestBase(object):
    def __init__(self, code, group, options):
        self.code = code
        self.group = group
        self.options = options

class TestSetup(TestBase):
    pass

class TestCode(TestBase):
    pass

class TestOutput(TestBase):
    pass

class TestCase(object):
    def __init__(self, setup, code, output):
        if setup:
            self.code = setup.code
            if setup.code[-1] != '\n':
                self.code += '\n' 
            self.code += code.code
        else:
            self.code = code.code
        if output:
            self.output = output.code
            self.options = output.options
        else:
            self.output = ''
            self.options = code.options
            
        # When we start handling groups, we want to get the group of the
        # test here, so we can put that in the test report, I think:
        self.group = ''
        
def parse(document):
    groups = {}
    previous_type = ''
    for region in document.find_regions(BLOCK_START, BLOCK_END):
        source = document.source[region.start_match.end():region.end_match.start()]
        source = textwrap.dedent(source).strip()
        document.claim_region(region)
        type_, extras = region.start_match.groups()
        group = ''
        options = None
        if extras:
            group = extras.splitlines()[0].strip()
            for option in extras.splitlines()[1:]:
                if ':options:' in option:
                    options = option.split(':options:')[1].strip()
                    break
        if type_ == 'setup':
            region.parsed = TestSetup(source, group, options)
        elif type_ == 'code':
            region.parsed = TestCode(source, group, options)
        elif type_ == 'output':
            region.parsed = TestOutput(source, group, options)
    
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

def evaluate(region, document, globs):
    if not isinstance(region.parsed, TestCase):
        return

    try:
        old_compile = doctest.compile
    except AttributeError:
        old_compile = compile
    doctest.compile = monkey_compile

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
            
    test_options = {doctest.ELLIPSIS: True,
                    doctest.IGNORE_EXCEPTION_DETAIL: True,
                    doctest.DONT_ACCEPT_TRUE_FOR_1: True,
                    }        
    options = region.parsed.options
    if options:
        for x in options.split(','):
            x = x.strip()
            sign = x[0]
            value = eval('doctest.' + x[1:])
            test_options[value] = sign == '+'        
    example = doctest.Example(region.parsed.code, output, exc_msg=exc_msg,
                              lineno=region.lineno, options=test_options)
    test = doctest.DocTest([example], globs, test_name, document.location,
                           region.lineno-1, None)
    runner = doctest.DocTestRunner()
    runner.DIVIDER = '' # disable unwanted result formatting
    runner.run(test, clear_globs=False)
    region.evaluated = result
    doctest.compile = old_compile
    

class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [parse], [evaluate])
