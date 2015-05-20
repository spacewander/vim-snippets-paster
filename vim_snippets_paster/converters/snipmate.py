from .snippet import Snippet

def parse(input, ct):
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

def build(snip):
    return snip

