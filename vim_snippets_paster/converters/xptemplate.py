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
        if 'hidden' in ct:
            self.hidden = ct['hidden']
        else:
            self.hidden = {}

        head, _, comment = input[0].partition('"')
        head = head.split()
        snip_name = head[1]
        self.x_attributes = {}
        cur_attr = ''
        for i, attr in enumerate(head[2:]):
            # unescape '\ '
            if attr.endswith('\\'):
                cur_attr = attr[:-1] + ' '
                continue
            cur_attr += attr
            name, _, value = cur_attr.partition('=')
            cur_attr = ''
            self.x_attributes[name] = value

        if 'hidden' in self.x_attributes:
            if 'hidden' not in ct:
                ct['hidden'] = {}
            # store the snippet body so that other snippets can include it
            ct['hidden'][snip_name] = '\n'.join(input[1:])
            self.snippets = []
            return

        # hint is like "description
        if comment == '' and 'hint' in self.x_attributes:
            comment = self.x_attributes['hint']
        # xpt-snippet-wrap(VISUAL placeholder)
        if 'wrap' in self.x_attributes:
            self.visual = self.x_attributes['wrap']
        elif 'wraponly' in self.x_attributes:
            self.visual = self.x_attributes['wraponly']
        else:
            self.visual = None

        # not implemented for XSET and XSETm yet, just ignore them
        body_lines = []
        fitered_xset_body = [l for l in input[1:] if not l.startswith('XSET ')]
        in_XSETm = False
        for line in fitered_xset_body:
            if line.startswith('XSETm END'):
                in_XSETm = False
                continue
            elif line.startswith('XSETm '):
                in_XSETm = True
            if not in_XSETm:
                body_lines.append(line)
        body = '\n'.join(body_lines)

        snip = Snippet('xptemplate', snip_name, body=self.parse_body(body),
                    description=self.unescape_description(comment.lstrip()))
        snip.x_attributes = self.x_attributes

        self.snippets = [snip]
        if 'alias' in self.x_attributes:
            alias = Snippet('xptemplate', self.x_attributes['alias'], body=snip.body,
                            description=snip.description)
            self.snippets.append(alias)
        elif 'synonym' in self.x_attributes:
            aliases = self.x_attributes['synonym'].split('|')
            self.snippets.extend(Snippet('xptemplate',
                                         alias_name, body=snip.body,
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
        if value in ('cursor', 'CURSOR'):
            return "$0"
        if value in ('$author', '$email'):
            return '`%s`' % value
        # In xptemplate, the syntax used to embed vimscript is the same as
        # one used to mark variable.
        # Because they share same vimscript context.
        # Therefore, it is not easy to distinguish embeded vimscript and variable.
        # Currently, if there is a function call inside,
        # we will treat it as embeded vimscript.
        if value.find('(') < value.find(')'): # function call inside
            return '`%s`' % value

        # xpt-snippet-wrap(VISUAL placeholder)
        if value == self.visual:
            if placeholder != '':
                return "${VISUAL:%s}" % placeholder
            return "$VISUAL"

        if value in PREDEFINED_VALUE:
            return PREDEFINED_VALUE[value]

        include_tp = ''
        if value[0] == ':' and value[-1] == ':':
            include_tp = value[1:-1]
        elif value.startswith('Include:'):
            include_tp = value[8:]
        if include_tp != '':
            # snippet name only supports \w, if '(' exists,
            # it will be 'Inclusion with parameter', which is not implemented yet.
            if '(' not in include_tp and include_tp in self.hidden:
                return self.parse_body(self.hidden[include_tp])
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

    def unescape_description(self, desc):
        """unescape \$ and \("""
        return desc.replace('\$', '$').replace('\(', '(')


def build(snip):
    return snip

