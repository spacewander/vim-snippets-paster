import itertools

from .snippet import Snippet

def make_converter(src, dest):
    """to make creating function in loop possible"""
    return lambda input: convert(src, dest, input)

types = ['snipmate', 'ultisnips', 'xptemplate']
for src, dest in itertools.permutations(types, 2):
        func = 'convert_%s_to_%s' % (src, dest)
        globals()[func] = make_converter(src, dest)

def convert(src, dest, input):
    if src == 'snipmate':
        snip = parse_snipmate(input)
    elif src == 'ultisnips':
        snip = parse_ultisnips(input)
    elif src == 'xptemplate':
        snip = parse_xptemplate(input)

    if dest == 'snipmate':
        return build_snipmate(snip)
    elif dest == 'ultisnips':
        return build_ultisnips(snip)
    elif dest == 'xptemplate':
        return build_xptemplate(snip)
    # impossible to reach here
    raise ValueError("unsupport snippet type %s got" % dest)

def parse_snipmate(input):
    return ""

def parse_ultisnips(input):
    return ""

def parse_xptemplate(input):
    """
    snippet format:
        XPT <snippetName> [name=value] [name=value] ..
        <snippet body>..
    """
    head = input[0]
    snip = Snippet(head.split()[1], '\n'.join(input[1:]))
    print(snip)
    return ""

def build_snipmate(snip):
    return snip

def build_ultisnips(snip):
    return ""

def build_xptemplate(snip):
    return ""

