import re

from .snippet import Snippet
from .ultility import (format_placeholders, NotImplementFeatureException,
                       embeded)

def preprocess_with_options(body, options):
    """
    preprocess the snippet body according to options before put into Snippet
    """
    options = set(options)

def handle_embeded_variables(body):
    def handle_embeded_variable(match):
        value = match.group(1)
        if value == '`g:snips_author`':
            return '$author'
        if value == '`g:snips_author_email`':
            return '$email'
        if value.startswith('!p '):
            raise NotImplementFeatureException(feature='embed python code')
        if value.startswith('!v '):
            return '`%s`' % value[3:]
        raise NotImplementFeatureException(feature='embed shell code')

    return re.sub(embeded, handle_embeded_variable, body)

def parse(input, ct):
    """
    snippet format:
        snippet "if xx" ["if ... then (if)" ["expression"] [options]]
        if ${2:[[ ${1:condition} ]]}; then
                ${0:#statements}
        fi
        endsnippet
    If a not implemented feature is parsed, raise a NotImplementFeatureException.
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
    body = format_placeholders(input[1:-1])
    preprocess_with_options(body, u_options)
    snip = Snippet('ultisnips', snip_name,
                   body=handle_embeded_variables('\n'.join(body)),
                   description=description)
    snip.u_options = u_options
    snip.u_context = context
    return snip


def build(snip):
    if snip.description != '':
        head = 'snippet %s "%s"\n' % (snip.name, snip.description)
    else:
        head = 'snippet %s\n' % snip.name
    body = build_body(snip.body)
    return head + body + "\nendsnippet"

def build_body(body):
    return body

