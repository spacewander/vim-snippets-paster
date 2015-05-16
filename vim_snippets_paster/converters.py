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
    """
    snippet[!] xxx [description]
        snippet body
    """
    def remove_indent(line):
        """remove the first level indent if there is any indent in the line"""
        return line

    head = input[0].split(' ', 2)
    if len(head) == 3:
        _, snip_name, description = head
    else:
        _, snip_name = head
        description = None
    snip = Snippet(snip_name, body='\n'.join(map(remove_indent, input[1:])),
                   description=description)
    print(snip)
    return snip

def parse_ultisnips(input):
    """
    snippet format:
        snippet "if xx" ["if ... then (if)"] [option]
        if ${2:[[ ${1:condition} ]]}; then
                ${0:#statements}
        fi
        endsnippet
    """
    base, _, extend = input[0].partition('"')
    _, snip_name = base.split(' ', 1)
    # extract pairs of char which work as quotes
    if snip_name[0] == snip_name[-1]:
        snip_name = snip_name[1:-1]

    if extend == '':
        description, u_options = None, None
    elif extend[-1] == '"':
        description, u_options = extend[:-1], None
    else:
        description, u_options = extend.rsplit(' ', 1)
        description = description[:-1]
    snip = Snippet(snip_name, body='\n'.join(input[1:-1]),
                   description=description)
    snip.u_options = u_options
    return snip

def parse_xptemplate(input):
    """
    snippet format:
        XPT _if [name] [name=value] [name=value] ..
        if`$SPcmd^(`$SParg^`condition^`$SParg^)`$BRif^{
            `cursor^
        }
    """
    head, _, comment = input[0].partition('"')
    head = head.split()
    snip_name = head[1]
    x_attributes = {}
    for attr in head[2:]:
        name, _, value = attr.partition('=')
        x_attributes[name] = value

    snip = Snippet(snip_name, body='\n'.join(input[1:]), description=comment)
    snip.x_attributes = x_attributes
    return snip

def build_snipmate(snip):
    return snip

def build_ultisnips(snip):
    return ""

def build_xptemplate(snip):
    return ""

