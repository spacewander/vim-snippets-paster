from .snippet import Snippet
from .ultility import UnsupportFeatureException

def parse(input, ct):
    """
    snippet[!] xxx [description]
        snippet body

    If a not implemented feature is parsed, raise a NotImplementFeatureException.
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

def build(snip):
    if len(snip.name.split()) > 1:
        raise UnsupportFeatureException("snipmate doesn't allow whitespace in snippet trigger")
    head = "snippet %s %s\n" % (snip.name, snip.description)
    body = map(lambda x: '\t' + x, snip.body.split('\n'))
    return head + '\n'.join(body)

