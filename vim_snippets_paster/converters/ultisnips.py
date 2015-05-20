from .snippet import Snippet

def parse(input, ct):
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

def build(snip):
    return snip

