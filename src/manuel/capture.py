import manuel
import re
import string
import textwrap

CAPTURE_DIRECTIVE = re.compile(r'^\.\.\s*->\s*(?P<name>\S+).*$', re.MULTILINE)


class Capture(object):
    def __init__(self, name, block):
        self.name = name
        self.block = block


@manuel.timing(manuel.EARLY)
def find_captures(document):
    for region in document.find_regions(CAPTURE_DIRECTIVE):
        # note that start and end have different bases, "start" is the offset
        # from the begining of the region, "end" is a document line number
        end = region.lineno-2

        # not that we've extracted the information we need, lets slice up the
        # document's regions to match

        for candidate in document:
            if candidate.lineno >= region.lineno:
                break
            found_region = candidate

        lines = found_region.source.splitlines()
        if found_region.lineno + len(lines) < end:
            raise RuntimeError('both start and end lines must be in the '
                'same region')

        for offset, line in reversed(list(enumerate(lines))):
            if offset > end - found_region.lineno:
                continue
            if line and line[0] in string.whitespace:
                start = offset
            if line and line[0] not in string.whitespace:
                break
        else:
            raise RuntimeError("couldn't find the start of the block")

        _, temp_region = document.split_region(found_region,
            found_region.lineno+start)

        # there are some extra lines in the new region, trim them off
        final_region, _ = document.split_region(temp_region, end+1)
        document.remove_region(final_region)

        name = region.start_match.group('name')
        block = textwrap.dedent(final_region.source)
        document.claim_region(region)
        region.parsed = Capture(name, block)


def store_capture(region, document, globs):
    if not isinstance(region.parsed, Capture):
        return

    globs[region.parsed.name] = region.parsed.block


class Manuel(manuel.Manuel):
    def __init__(self):
        manuel.Manuel.__init__(self, [find_captures], [store_capture])
