import re

from functools import reduce

from .snippet import Snippet
from .ultility import (NotImplementFeatureException,
                       UnsupportFeatureException, embeded,
                       format_placeholders)

Filename_pattern = re.compile('Filename\((.*?)\)')
def handle_Filename(match):
    expr = match.group(0)
    if re.search(Filename_pattern, expr) is not None:
        raise NotImplementFeatureException(feature='Filename')
    return expr

def preproccess_vimscript(lines):
    return [re.sub(embeded, handle_Filename, line) for line in lines]

def handle_embeded_variables(body):
    def handle_embeded_variable(match):
        value = match.group(1)
        if value == 'g:snips_author':
            return '`$author`'
    return re.sub(embeded, handle_embeded_variable, body)

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
                   body=handle_embeded_variables(body),
                   description=description)
    return snip


def build(snip):
    if len(snip.name.split()) > 1:
        raise UnsupportFeatureException(
            "snipmate doesn't allow whitespace in snippet trigger")
    head = "snippet %s %s\n" % (snip.name, snip.description)
    body = build_body(snip.body)
    return head + body

def build_body(body):
    fs = [convert_embeded_variables, convert_placeholders, append_indent]
    return reduce(lambda x, f: f(x), fs, body)

def convert_embeded_variables(body):
    def handle_embeded_variable(match):
        value = match.group(1)
        if value == '$author':
            return '`g:snips_author`'
        if value == '$email':
            raise UnsupportFeatureException(feature='$email')
        return '`%s`' % value

    return re.sub(embeded, handle_embeded_variable, body)

def convert_placeholders(body):
    return body

def append_indent(body):
    return "".join(map(lambda x: '\t' + x, body.splitlines(True)))
