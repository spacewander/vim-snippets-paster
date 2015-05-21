import itertools

from . import snipmate
from . import ultisnips
from . import xptemplate
from .ultility import NotImplementFeatureException, UnsupportFeatureException

def make_converter(src, dest):
    """to make creating function in loop possible"""
    return lambda input, ct: convert(src, dest, input, ct)

types = ['snipmate', 'ultisnips', 'xptemplate']
for src, dest in itertools.permutations(types, 2):
        func = 'convert_%s_to_%s' % (src, dest)
        globals()[func] = make_converter(src, dest)

def convert(src, dest, input, ct):
    """
    convert input text into a snippet instance according to src type,
    and build it back to text according to dest type.

    :ct     the global context needed in parsing
    """
    try:
        if src == 'snipmate':
            snip = snipmate.parse(input, ct)
            return build(snip, dest)
        elif src == 'ultisnips':
            snip = ultisnips.parse(input, ct)
            return build(snip, dest)
        elif src == 'xptemplate':
            snips = xptemplate.parse(input, ct)
            # because the 'hidden', 'alias' and 'synonym' attributes,
            # there may be no, one, or multiple parsed results
            return "\n\n".join(build(s, dest) for s in snips)

    except NotImplementFeatureException as e:
        if src == 'xptemplate':
            comment = '"'
        else:
            comment = '#'
        output = "%s%s\n" % (comment, e)
        for line in input:
            output += "%s%s\n" % (comment, line)
        return output
    # impossible to reach here
    raise ValueError("unsupport snippet type %s got" % dest)


def build(snippet, dest):
    try:
        if dest == 'snipmate':
            return snipmate.build(snippet)
        elif dest == 'ultisnips':
            return ultisnips.build(snippet)
        elif dest == 'xptemplate':
            return xptemplate.build(snippet)
    except UnsupportFeatureException as e:
        if src == 'xptemplate':
            comment = '"'
        else:
            comment = '#'
        output = "%s%s\n" % (comment, e)
        for line in input:
            output += "%s%s\n" % (comment, line)
        return output

