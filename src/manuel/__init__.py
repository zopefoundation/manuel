import imp
import re


def absolute_import(name):
    return imp.load_module(name, *imp.find_module(name))


def newlineify(s):
    if s[-1] != '\n':
        s += '\n'
    return s


class Region(object):
    """A portion of source found via regular expression."""

    parsed = None
    evaluated = None
    formatted = None

    def __init__(self, lineno, source, start_match=None, end_match=None,
            provenance=None):
        self.lineno = lineno
        self.source = newlineify(source)
        self.start_match = start_match
        self.end_match = end_match
        self.provenance = provenance

    def copy(self):
        """Private utility function to make a copy of this region.
        """
        copy = Region(self.lineno, self.source, provenance=self.provenance)
        copy.parsed = self.parsed
        copy.evaluated = self.evaluated
        copy.formatted = self.formatted
        return copy


def find_line(region, index):
    return region[:index].count('\n') + 1


def check_region_start(region, match):
    if match.start() != 0 \
    and region.source[match.start()-1] != '\n':
        raise ValueError(
            'Regions must start at the begining of a line.')


def check_region_end(region, match):
    if match.end() != len(region.source) \
    and region.source[match.end()] != '\n':
        raise ValueError(
            'Regions must end at the ending of a line.')


def lines_to_string(lines):
    return '\n'.join(lines) + '\n'


def make_string_into_lines(s):
    lines = newlineify(s).split('\n')
    assert lines[-1] == ''
    del lines[-1]
    return lines


def break_up_region(original, new, parsed):
    assert original.parsed is None
    lines = make_string_into_lines(original.source)

    new_regions = []

    # figure out if there are any lines before the given region
    before_lines = lines[:new.lineno-original.lineno]
    if before_lines:
        new_regions.append(
            Region(original.lineno, lines_to_string(before_lines)))

    # put in the parsed
    new.parsed = parsed
    new_regions.append(new)

    # figure out if there are any lines after the given region
    assert new.source[-1] == '\n', 'all lines must end with a newline'
    lines_in_new = new.source.count('\n')
    after_lines = lines[len(before_lines)+lines_in_new:]
    if after_lines:
        first_line_after_new = new.lineno + lines_in_new
        new_regions.append(
            Region(first_line_after_new, lines_to_string(after_lines)))

    assert original.source.count('\n') == \
        sum(r.source.count('\n') for r in new_regions)
    return new_regions


class Document(object):

    def __init__(self, source, location='<memory>'):
        self.source = newlineify(source)
        self.location = location

        self.regions = [Region(lineno=1, source=source)]
        self.shadow_regions = []

    def find_regions(self, start, end=None):
        def compile(regex):
            if regex is not None and isinstance(regex, basestring):
                regex = re.compile(regex)
            return regex

        start = compile(start)
        end = compile(end)

        results = []
        for region in self.regions:
            # can't parse things that have already been parsed
            if region.parsed:
                continue

            for start_match in re.finditer(start, region.source):
                first_lineno = region.lineno + find_line(
                    region.source, start_match.start()) - 1
                check_region_start(region, start_match)

                if end is None:
                    end_match = None
                    check_region_end(region, start_match)
                    text = start_match.group()
                else:
                    end_match = end.search(region.source, start_match.end())
                    check_region_end(region, end_match)
                    text = region.source[start_match.start():end_match.end()]

                if text[-1] != '\n':
                    text += '\n'

                new_region = Region(first_lineno, text, start_match, end_match)
                self.shadow_regions.append(new_region)
                results.append(new_region)

        return results

    def split_region(self, region, lineno):
        lineno -= region.lineno
        assert lineno > 0
        assert region in self.regions
        assert region.parsed == region.evaluated == region.formatted == None
        lines = make_string_into_lines(region.source)
        source1 = lines_to_string(lines[:lineno])
        source2 = lines_to_string(lines[lineno:])
        region_index = self.regions.index(region)
        del self.regions[region_index]
        lines_in_source1 = source1.count('\n')
        region1 = Region(region.lineno, source1)
        region2 = Region(region.lineno+lines_in_source1, source2)
        self.regions.insert(region_index, region2)
        self.regions.insert(region_index, region1)
        return region1, region2

    # XXX this method needs a better name
    def replace_region(self, to_be_replaced, parsed):
        new_regions = []
        old_regions = list(self.regions)
        while old_regions:
            region = old_regions.pop(0)
            if region.lineno == to_be_replaced.lineno:
                assert not region.parsed
                new_regions.extend(break_up_region(
                    region, to_be_replaced, parsed))
                break
            elif region.lineno > to_be_replaced.lineno: # we "overshot"
                assert not new_regions[-1].parsed
                to_be_broken = new_regions[-1]
                del new_regions[-1]
                new_regions.extend(break_up_region(
                    to_be_broken, to_be_replaced, parsed))
                new_regions.append(region)
                break

            new_regions.append(region)
        else:
            # we didn't make any replacements, so the parsed data must be for
            # the very last region, which also must not have been parsed yet
            assert not region.parsed
            del new_regions[-1]
            new_regions.extend(break_up_region(
                region, to_be_replaced, parsed))

        new_regions.extend(old_regions)
        self.regions = new_regions

    def insert_region(self, where, marker_region, new_region):
        if new_region in self.regions:
            raise ValueError(
                'Only regions not already in the document may be inserted.')
        if new_region in self.shadow_regions:
            raise ValueError(
                'Regions regurned by "find_regions" can not be directly '
                'inserted into a document.  Use "replace_region" instead.')

        for index, region in enumerate(self.regions):
            if region is marker_region:
                if where == 'after':
                    index += 1
                self.regions.insert(index, new_region)
                break

    def remove_region(self, region):
        self.regions.remove(region)

    def insert_region_before(self, marker_region, new_region):
        self.insert_region('before', marker_region, new_region)

    def insert_region_after(self, marker_region, new_region):
        self.insert_region('after', marker_region, new_region)


    def do_with(self, things):
        """Private helper for other do_* functions.
        """
        for timing, thing in sorted(things):
            thing(self)

    def parse_with(self, m):
        self.do_with(m.parsers)

    def evaluate_with(self, m):
        self.do_with(m.evaluaters)

    def format_with(self, m):
        self.do_with(m.formatters)

    def process_with(self, m):
        """Run all phases of document processing using a Manuel instance.
        """
        self.parse_with(m)
        self.evaluate_with(m)
        self.format_with(m)

    def formatted(self):
        """Return a string of all non-boolean-false formatted regions.
        """
        return ''.join(region.formatted for region in self if region.formatted)

    def __iter__(self):
        """Iterate over all regions of the document.
        """
        return iter(self.regions)


class Manuel(object):

    def __init__(self):
        self.parsers = []
        self.evaluaters = []
        self.formatters = []

    def parser(self, func=None, timing=None):
        return self.thinger(self.parsers, func, timing)

    def evaluater(self, func=None, timing=None):
        return self.thinger(self.evaluaters, func, timing)

    def formatter(self, func=None, timing=None):
        return self.thinger(self.formatters, func, timing)

    def thinger(self, things, func, timing):
        """Private helper for adding functions to a phase.
        """
        if func is None:
            # the decorator is being called prior to being used as a decorator,
            # return a callable that can be called to provide the function
            # to be decorated
            return lambda func: self.thinger(things, func, timing=timing)

        assert timing in ('early', 'late', None)
        if timing == None:
            # arbitrarily chosen string that sorts between "early" and "late"
            timing = 'k'

        things.append((timing, func))

    def extend(self, other):
        self.parsers.extend(other.parsers)
        self.evaluaters.extend(other.evaluaters)
        self.formatters.extend(other.formatters)
