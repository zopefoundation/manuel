import manuel
import re
import sys
import new
import textwrap

FAKE_MODULE_START = re.compile(
        r'^\.\.\s*module-block::?\s*(?P<module_name>[a-zA-Z_]*)',
        re.MULTILINE)
FAKE_MODULE_END = re.compile(r'(\n\Z|\n(?=\S))')
MODULE_NS = "manueltest.fake"

# To store our fake module's lines
class FakeModuleSnippet(object):
    def __init__(self, code, module_name):
        self.code = code
        self.module_name = module_name

def find_fakes(document):
    for region in document.find_regions(FAKE_MODULE_START, FAKE_MODULE_END):
        if region.parsed:
            continue

        module_name = region.start_match.group('module_name')
        # Sanitise indentation
        source = textwrap.dedent('\n'.join(region.source.splitlines()[1:]))
        source_location = '%s:%d' % (document.location, region.lineno)

        code = compile(source, source_location, 'exec')
        document.claim_region(region)
        region.parsed = FakeModuleSnippet(code, module_name)

def execute_into_module(region, document, doc_globs):
    if not isinstance(region.parsed, FakeModuleSnippet):
        return

    # build a suitable module
    module_name = region.parsed.module_name
    full_module_name = MODULE_NS + "." + module_name
    module = new.module(full_module_name)
    module_name_parts = full_module_name.split('.')
    module.__file__ = '/' + '/'.join(module_name_parts)

    # Make the module also available through normal import
    if not MODULE_NS in sys.modules:
        sys.modules['manueltest'] = new.module('manueltest')
        sys.modules['manueltest.fake'] = new.module('manueltest.fake')
        sys.modules['manueltest'].fake = sys.modules['manueltest.fake']

    exec region.parsed.code in module.__dict__
    # XXX Do I want del module['__builtin__']??

    # Make the module visible and usable in the given name
    doc_globs[module_name] =  module

    sys.modules[full_module_name] = module
    setattr(sys.modules['manueltest.fake'], full_module_name.split('.')[-1],
            module)

class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_fakes], [execute_into_module])
