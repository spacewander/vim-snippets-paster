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

    Feature:
    snipmate:
        * special variable, like g:snips_author
        * mirror
        * transformations
        * vimscript evalution
        * tab stop(${1:xxx}, $0, and so on)
        * VISUAL stop(${VISUAL:blah})
        * snippet description
    ultisnips:
        * special variable, like $author, $email
        * mirror
        * transformations
        * evalution(vimscript, shell, python)
        * tab stop
        * VISUAL stop
        * snippet description
        * snippet trigger can contain whitespace
        * snippet options
        * snippet context
    xptemplate:
        * special variable, like $author, $email
        * variable
        * snippet description
        * vimscript evalution
        * attributes(hint/hidden/alias/wrap/...)
        * included snippet
        * XSET

    If a feature is not implemented, the relative part will be commented.
    (A feature not implemented is a feature only supported by given src type)
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
    """
    Build a snippet of dest type from a Snippet object constructed from snippet
    text of src type.

    If a feature is unsupport, return commented snippet text.
    (A unsupport feature is a feature not supported by dest type)
    """
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

