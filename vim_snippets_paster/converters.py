import itertools

from .snippet import Snippet

def make_converter(src, dest):
    """to make creating function in loop possible"""
    return lambda input: convert(src, dest, input)

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
        snip = parse_snipmate(input, ct)
    elif src == 'ultisnips':
        snip = parse_ultisnips(input, ct)
    elif src == 'xptemplate':
        snip = parse_xptemplate(input, ct)

    if dest == 'snipmate':
        return build_snipmate(snip)
    elif dest == 'ultisnips':
        return build_ultisnips(snip)
    elif dest == 'xptemplate':
        return build_xptemplate(snip)
    # impossible to reach here
    raise ValueError("unsupport snippet type %s got" % dest)

def parse_snipmate(input, ct):
    """
    snippet[!] xxx [description]
        snippet body
    """
    indent_size = len(input[1]) - len(input[1].lstrip())
    def remove_indent(line):
        """remove the first level indent"""
        return line[indent_size:]

    head = input[0].split(' ', 2)
    if len(head) == 3:
        _, snip_name, description = head
    else:
        _, snip_name = head
        description = ''
    snip = Snippet('snipmate', snip_name,
                   body='\n'.join(map(remove_indent, input[1:])),
                   description=description)
    return snip

def parse_ultisnips(input, ct):
    """
    snippet format:
        snippet "if xx" ["if ... then (if)" ["expression"] [options]]
        if ${2:[[ ${1:condition} ]]}; then
                ${0:#statements}
        fi
        endsnippet
    """
    # https://github.com/SirVer/ultisnips/blob/master/pythonx/UltiSnips/snippet/source/file/ultisnips.py
    # know how to parse from function _handle_snippet_or_global, thanks for SirVer
    head = input[0][len('snippet '):].strip()
    words = head.split()

    u_options = ''
    if len(words) > 2:
        # second to last word ends with a quote
        if '"' not in words[-1] and words[-2][-1] == '"':
            u_options = words[-1]
            head = head[:-len(u_options) - 1].rstrip()

    context = None
    if 'e' in u_options:
        left = head[:-1].rfind('"')
        if left != -1 and left != 0:
            context, head = head[left:].strip('"'), head[:left]

    # Get and strip description if it exists
    head = head.strip()
    description = ''
    if len(head.split()) > 1 and head[-1] == '"':
        left = head[:-1].rfind('"')
        if left != -1 and left != 0:
            description, head = head[left:], head[:left]

    # The rest is the snip_name
    snip_name = head.strip()
    # always, the code believe the syntax of snippet is definitely true.
    # don't disappoint it!

    snip = Snippet('ultisnips', snip_name, body='\n'.join(input[1:-1]),
                   description=description)
    snip.u_options = u_options
    snip.u_context = context
    print(snip)
    return snip

def parse_xptemplate(input, ct):
    """
    snippet format:
        XPT [_]if [name] [name=value] [name=value] ..
        if`$SPcmd^(`$SParg^`condition^`$SParg^)`$BRif^{
            `cursor^
        }
    """
    def convert_xptemplate_placeholder(body):
        """
        convert the xptemplate style placeholder(`value^placeholder^) to normal
        one(${order:placeholder})
        """
        return body

    head, _, comment = input[0].partition('"')
    head = head.split()
    snip_name = head[1]
    x_attributes = {}
    for attr in head[2:]:
        name, _, value = attr.partition('=')
        x_attributes[name] = value

    body = '\n'.join(input[1:])
    snip = Snippet('xptemplate', snip_name,
                   body=convert_xptemplate_placeholder(body),
                   description=comment)
    snip.x_attributes = x_attributes
    return snip

def build_snipmate(snip):
    return snip

def build_ultisnips(snip):
    return snip

def build_xptemplate(snip):
    return snip

