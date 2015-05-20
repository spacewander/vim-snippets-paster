import re

from .snippet import Snippet

PREDEFINED_VALUE = {
    '$SParg':   ' ',
    '$SPop':    ' ',
}

def parse(input, ct):
    return XptemplateParser(input, ct).snippet

class XptemplateParser(object):
    def __init__(self, input, ct):
        """
        snippet format:
            XPT [_]if [name] [name=value] [name=value] ..
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

        body = '\n'.join(input[1:])
        snip = Snippet('xptemplate', snip_name, body=self.parse_body(body),
                    description=comment)
        snip.x_attributes = x_attributes
        self.snippet = snip

    def parse_body(self, body):
        """parse the snippet body, convert it to snipmate-like format"""
        self.order = 0
        self.parsed_value = {}
        body = self.convert_xptemplate_placeholders(body)
        return body

    def convert_xptemplate_placeholder(self, match):
        """
        :match is a MatchObject contains the valu inside `^
        """
        # match.group(1) may be 'value^placeholder' or 'value'
        value, _, placeholder = match.group(1).partition('^')
        if value in PREDEFINED_VALUE:
            return PREDEFINED_VALUE[value]

        if value not in self.parsed_value:
            self.order += 1
        order = self.parsed_value.setdefault(value, self.order)
        if placeholder != '':
            return "${%d:%s}" % (order, placeholder)
        return "${%d:%s}" % (order, value)

    def convert_xptemplate_placeholders(self, body):
        """
        convert the xptemplate style placeholder(`value^placeholder^) to
        snipmate-like one(${order:placeholder})
        """
        p = re.compile('`([^^]+\^?\w*?)\^')
        r = re.sub(p, self.convert_xptemplate_placeholder, body)
        print(r)
        return r


def build(snip):
    return snip

