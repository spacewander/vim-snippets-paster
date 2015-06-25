import re

from functools import reduce

from . import ultility
from .snippet import Snippet
from .ultility import (NotImplementFeatureException,
                       UnsupportFeatureException, embeded,
                       format_placeholders)

Filename_pattern = re.compile('Filename\((.*?)\)')

def parse_embeded_variables(body):
    """deal with embeded variables in parse setup"""
    def handle_embeded_variable(match):
        value = match.group(0)
        if value == '`g:snips_author`':
            return '`$author`'
        if re.search(Filename_pattern, value) is not None:
            raise NotImplementFeatureException(feature='Filename')
        return value
    return re.sub(embeded, handle_embeded_variable, body)

def parse_placeholders(body):
    if re.search(ultility.transformation, body) is not None:
        raise NotImplementFeatureException("""
        snipmate use vim's substitute to transform variable,
        you may need to look up the docs and convert the transform syntax.""")
    return body

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

    body_filters = [remove_indent, format_placeholders]
    body = '\n'.join(reduce(lambda x, f: f(x), body_filters, input[1:]))

    snip = Snippet('snipmate', snip_name,
                   body=parse_placeholders(
                        parse_embeded_variables(body)),
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
    fs = [build_embeded_variables, append_indent]
    return reduce(lambda x, f: f(x), fs, body)

def build_embeded_variables(body):
    """deal with embeded variables in build setup"""
    def handle_embeded_variable(match):
        value = match.group(1)
        if value == '$author':
            return '`g:snips_author`'
        if value == '$email':
            raise UnsupportFeatureException(feature='$email')
        return '`%s`' % value

    return re.sub(embeded, handle_embeded_variable, body)

def append_indent(body):
    return "".join(map(lambda x: '\t' + x, body.splitlines(True)))

