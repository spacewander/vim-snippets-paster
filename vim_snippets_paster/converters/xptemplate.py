import re

from .snippet import Snippet
from .ultility import NotImplementFeatureException

PREDEFINED_VALUE = {
    '$SParg':   ' ',
    '$SPop':    ' ',
    '$VOID':    '',
    '$BRif':    ' ',
    '$BRel':    '\n',
    '$BRloop':  ' ',
    '$BRstc':   ' ',
    '$BRfun':   ' ',
    '$SPfun':   '',
    '$SPcmd':   ' ',
    '$TRUE':    '1',
    '$FALSE':   '0',
    '$NULL':    '0',
    '$UNDEFINED': '0',
    '$VOID_LINE': '',
    '$CURSOR_PH': 'CURSOR',
    '$DATE_FMT': '%Y %b %d',
    '$TIME_FMT': '"%H:%M:%S"',
    '$DATETIME_FMT': '%c'
}

def parse(input, ct):
    """
    If a not implemented feature is parsed, raise a NotImplementFeatureException.
    Unlike other type of parser, this will return a list of snippets
    """
    return XptemplateParser(input, ct).snippets

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
        self.x_attributes = {}
        for attr in head[2:]:
            name, _, value = attr.partition('=')
            self.x_attributes[name] = value

        if 'hidden' in self.x_attributes:
            raise NotImplementFeatureException(feature='xpt-snippet-hidden')
        if 'wrap' in self.x_attributes:
            self.visual = self.x_attributes['wrap']
        elif 'wraponly' in self.x_attributes:
            self.visual = self.x_attributes['wraponly']
        else:
            self.visual = None

        body = '\n'.join(input[1:])
        snip = Snippet('xptemplate', snip_name, body=self.parse_body(body),
                    description=comment)
        snip.x_attributes = self.x_attributes

        self.snippets = [snip]
        if 'alias' in self.x_attributes:
            alias = Snippet('xptemplate', self.x_attributes['alias'], body=snip.body,
                            description=snip.description)
            self.snippets.append(alias)
        elif 'synonym' in self.x_attributes:
            aliases = self.x_attributes['synonym'].split('|')
            self.snippets.extend(Snippet('xptemplate', alias_name, body=snip.body,
                                         description=snip.description)
                                 for alias_name in aliases)
        # TODO: abbr


    def parse_body(self, body):
        """parse the snippet body, convert it to snipmate-like format"""
        self.order = 0
        self.parsed_value = {}
        body = self.convert_xptemplate_placeholders(body)
        return body

    def convert_xptemplate_placeholder(self, match):
        """
        :match is a MatchObject contains the value inside `^
        """
        # match.group(1) may be 'value^placeholder' or 'value'
        value, _, placeholder = match.group(1).partition('^')
        # filter specific value
        if value == 'cursor':
            return "$0"
        if value in ('$author', '$email'):
            raise NotImplementFeatureException(
                "parsing user defined variable %s not implemented" % value)

        # xpt-snippet-wrap(VISUAL placeholder)
        if value == self.visual:
            if placeholder != '':
                return "${VISUAL:%s}" % placeholder
            return "${VISUAL}"

        if value in PREDEFINED_VALUE:
            return PREDEFINED_VALUE[value]

        if (value[0] == ':' and value[-1] == ':') or value.startswith('Include:'):
            raise NotImplementFeatureException(feature="xpt-snippet-include")

        if value not in self.parsed_value:
            self.order += 1
            self.parsed_value[value] = self.order
            if placeholder != '':
                return "${%d:%s}" % (self.order, placeholder)
            return "${%d:%s}" % (self.order, value)
        else:
            return "$%s" % self.parsed_value[value]

    def convert_xptemplate_placeholders(self, body):
        """
        convert the xptemplate style placeholder(`value^placeholder^) to
        snipmate-like one(${order:placeholder})
        """
        p = re.compile('`([^^]+\^?\w*?)\^')
        r = re.sub(p, self.convert_xptemplate_placeholder, body)
        return r


def build(snip):
    return snip

