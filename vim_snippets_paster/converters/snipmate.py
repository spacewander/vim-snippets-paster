import re

from functools import reduce

from .snippet import Snippet
from .ultility import (NotImplementFeatureException,
                       UnsupportFeatureException, embeded)

def format_placeholders(lines):
    """convert ${0} and ${VISUAL} to $0 and $VISUAL"""
    return [line.replace('${0}', '$0').replace('${VISUAL}', '$VISUAL') \
            for line in lines]

Filename_pattern = re.compile('Filename\((.*?)\)')
def handle_Filename(match):
    expr = match.group(0)
    if re.match(Filename_pattern, expr):
        raise NotImplementFeatureException(feature='Filename')
    return expr

def preproccess_vimscript(lines):
    return [re.sub(embeded, handle_Filename, line) for line in lines]

def parse(input, ct):
    """
    snippet[!] xxx [description]
        snippet body

    If a not implemented feature is parsed, raise a NotImplementFeatureException.
    """
    indent_size = len(input[1]) - len(input[1].lstrip())
    def remove_indent(lines):
        """remove the first level indent"""
        return [line[indent_size:] for line in lines]

    head = input[0].split(' ', 2)
    if len(head) == 3:
        _, snip_name, description = head
    else:
        _, snip_name = head
        description = ''

    body_filters = [remove_indent, format_placeholders,
                    preproccess_vimscript]
    body = '\n'.join(reduce(lambda x, f: f(x), body_filters, input[1:]))

    snip = Snippet('snipmate', snip_name,
                   body=body, description=description)
    return snip


def build(snip):
    if len(snip.name.split()) > 1:
        raise UnsupportFeatureException(
            "snipmate doesn't allow whitespace in snippet trigger")
    head = "snippet %s %s\n" % (snip.name, snip.description)
    body = build_body(snip.body)
    body = map(lambda x: '\t' + x, body.split('\n'))
    return head + '\n'.join(body)

def build_body(body):
    fs = [convert_embeded_variable, convert_placeholder]
    return reduce(lambda x, f: f(x), fs, body)

def convert_embeded_variable(body):
    def handle_embeded_variable(match):
        value = match.group(1)
        if value == '$author':
            return '`g:snips_author`'
        if value == '$email':
            raise UnsupportFeatureException(feature='$email')
        if value.startswith('!p '):
            raise UnsupportFeatureException(feature='embed python code')
        if value.startswith('!s '):
            raise UnsupportFeatureException(feature='embed shell code')
        return '`%s`' % value

    return re.sub(embeded, handle_embeded_variable, body)

def convert_placeholder(body):
    return body

