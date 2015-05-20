import itertools

import snipmate
import ultisnips
import xptemplate

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
    if src == 'snipmate':
        snip = snipmate.parse(input, ct)
    elif src == 'ultisnips':
        snip = ultisnips.parse(input, ct)
    elif src == 'xptemplate':
        snip = xptemplate.parse(input, ct)

    if dest == 'snipmate':
        return snipmate.build(snip)
    elif dest == 'ultisnips':
        return ultisnips.build(snip)
    elif dest == 'xptemplate':
        return xptemplate.build(snip)
    # impossible to reach here
    raise ValueError("unsupport snippet type %s got" % dest)

