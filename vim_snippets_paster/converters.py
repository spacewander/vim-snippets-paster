import itertools

def make_converter(src, dest):
    """to make creating function in loop possible"""
    return lambda input: convert(src, dest, input)

types = ['snipmate', 'ultisnips', 'xptemplate']
for src, dest in itertools.permutations(types, 2):
        func = 'convert_%s_to_%s' % (src, dest)
        globals()[func] = make_converter(src, dest)

def convert(src, dest, input):
    return "%s %s %s" % (src, dest, input)
