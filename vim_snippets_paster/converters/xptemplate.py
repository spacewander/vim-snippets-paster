import re

from . import ultility
from .snippet import Snippet
from .ultility import (NotImplementFeatureException,
                       UnsupportFeatureException, embeded)

PREDEFINED_VALUE = {
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

        self.values = {}
        self.order = 0
        body_lines = []
        # comment out XSET/XSETm
        # remove repeation(`...^)
        # and also handle ComeFirst/ComeLast
        in_XSETm = False
        for line in input[1:]:
            if line.startswith('XSETm END'):
                in_XSETm = False
                continue
            elif line.startswith('XSETm '):
                in_XSETm = True
            if not in_XSETm:
                if line.startswith('XSET '):
                    _, expr = line.split(None, 1)
                    # XSET ComeFirst=0 len
                    if expr.startswith('ComeFirst='):
                        _, values = expr.split('=', 1)
                        values = values.split(' ')
                        for i, value in enumerate(values):
                            self.values[value] = i + 1
                        self.order += len(values)
                    elif expr.startswith('ComeLast='):
                        _, values = expr.split('=', 1)
                        for i, value in enumerate(values.split(' ')):
                            self.values[value] = -(i + 1)
                    else:
                        body_lines.append('#' + line)
                elif not line.lstrip().startswith('`...^'):
                    body_lines.append(line)
            else:
                body_lines.append('#' + line)
        body = '\n'.join(body_lines)

        # handle XPTvar
        self.var = {
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
        for name in ct:
            if name.startswith('$'):
                self.var[name] = ct[name]

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
        elif 'syn' in self.x_attributes: # syn is alias of synonym
            aliases = self.x_attributes['syn'].split('|')
            self.snippets.extend(Snippet('xptemplate',
                                         alias_name, body=snip.body,
                                         description=snip.description)
                                 for alias_name in aliases)
        # ignore abbr


    def parse_body(self, body):
        """parse the snippet body, convert it to snipmate-like format"""
        self.edge_magic_numer = "Append_this-toedge_value"
        body = self.convert_edge_placeholders(body)
        return self.convert_xptemplate_placeholders(body)

    def convert_edge_placeholders(self, body):
        edge_with_placeholder = re.compile(
                '`([^^`]*)`([^^`]*)`([^^]*)\^([^^`]*)\^')
        r = re.sub(edge_with_placeholder,
                r"\1`%s\2^\4^\3" % self.edge_magic_numer, body)
        edge = re.compile('`([^^`]*)`([^^`]*)`([^^]*)\^')
        r = re.sub(edge, r"\1`%s\2^\3" % self.edge_magic_numer, r)

        left_only_edge_with_placeholder = re.compile(
                '`([^^`]*)`([^^]*)\^([^^`]*)\^')
        r = re.sub(left_only_edge_with_placeholder,
                r"\1`%s\2^\3^" % self.edge_magic_numer, r)
        left_only_edge = re.compile('`([^^`]*)`([^^`]*)\^')
        return re.sub(left_only_edge, r"\1`%s\2^" % self.edge_magic_numer, r)

    def convert_placeholder(self, match):
        """
        :match is a MatchObject contains the value inside `^
        """
        # match.group(1) may be 'value^placeholder' or 'value'
        value, _, placeholder = match.group(1).partition('^')
        # filter specific value
        if value in ('cursor', 'CURSOR'):
            return "${0}"
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

        if value in self.var:
            return self.var[value]

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

        # Handle the order of placeholder with edge
        should_set_edge = False
        if value.startswith(self.edge_magic_numer):
            value = value[len(self.edge_magic_numer):]
            should_set_edge = True
        self.order_counter[value] = self.order_counter.setdefault(value, 0) + 1
        if should_set_edge:
            self.edge[value] = self.order_counter[value]

        # Update self.value so that we can use it in next parser
        if value not in self.values:
            self.order += 1
            self.values[value] = self.order
        if placeholder != '':
            return "`%s^%s^" % (value, placeholder)
        else:
            return "`%s^" % value

    def convert_value(self, match):
        """
        :match is a MatchObject contains the value inside `^
        """
        # match.group(1) may be 'value^placeholder' or 'value'
        value, _, placeholder = match.group(1).partition('^')
        if value in self.order_counter:
            self.order_counter[value] -= 1
            if self.order_counter[value] == 0:
                order = self.values[value]
                if placeholder != '':
                    return "${%d:%s}" % (order, placeholder)
                return "${%d:%s}" % (order, value)
            else:
                return "$%d" % self.values[value]
        raise ValueError("all values should has its own order_counter")

    def convert_xptemplate_placeholders(self, body):
        """
        convert the xptemplate style placeholder(`value^placeholder^) to
        snipmate-like one(${order:placeholder})
        """
        self.order_counter = {}
        self.edge = {}

        placeholder_pattern = re.compile('`([^^`]+\^?[^^`]*)\^')
        r = re.sub(placeholder_pattern, self.convert_placeholder, body)
        for value in self.values:
            order = self.values[value]
            if order < 0: # value in ComeLast
                self.values[value] = self.order - order
        # placeholder with edge should be the first, so reset counter here
        for value in self.order_counter:
            if value not in self.edge:
                self.order_counter[value] = 1
            else:
                self.order_counter[value] = self.edge[value]
        return re.sub(placeholder_pattern, self.convert_value, r)

    def unescape_description(self, desc):
        """unescape \$ and \("""
        return desc.replace('\$', '$').replace('\(', '(')


def build(snip):
    if len(snip.name.split()) > 1:
        raise UnsupportFeatureException(
            "xptemplate doesn't allow whitespace in snippet trigger")
    head = 'XPT %s' % snip.name
    builder = XptemplateBuilder(snip)
    if builder.hasWrap:
        head += " wrap=%s" % builder.wrap
    if snip.description != '':
        head += ' "%s' % snip.description
    return head + '\n' + builder.body + '\n...XPT'

class XptemplateBuilder(object):
    def __init__(self, snippet):
        self.body = snippet.body
        self.hasWrap = False
        self.wrap = ''
        self.convert_embeded_variables()
        self.convert_placeholders()

    def convert_embeded_variables(self):
        def handle_embeded_variable(match):
            value = match.group(1)
            if value == '$author':
                return '`$author^'
            if value == '$email':
                return '`$email^'
            return '`%s^' % value
        self.body = re.sub(embeded, handle_embeded_variable, self.body)

    def convert_placeholders(self):
        placeholders = re.findall(ultility.placeholder, self.body)
        # since transformation is not implemented, there are four cases:
        # 1. ${1}
        # 2. ${1:some}
        # 3. ${VISUAL}
        # 4. ${VISUAL:some}
        tabstop2placeholders = {}
        for placeholder in placeholders:
            if not placeholder.startswith('VISUAL'):
                colon = placeholder.find(':')
                if colon != -1:
                    tabstop2placeholders[placeholder[:colon]] = \
                            placeholder[colon+1:]

        self.counter = 'h'
        def handle_placeholder(match):
            global counter
            value = match.group(1)
            if value.startswith('VISUAL'):
                self.hasWrap = True
                colon = value.find(':')
                if colon != -1:
                    self.wrap = value[colon+1:]
                else:
                    self.wrap = 'VISUAL'
                placeholder = self.wrap
            elif value.isdigit():
                if value == '0':
                    placeholder = 'cursor'
                elif value in tabstop2placeholders:
                    placeholder = tabstop2placeholders[value]
                else:
                    # add prefix make it safier, but dirty
                    self.counter = chr(ord(self.counter) + 1)
                    placeholder = self.counter
            else:
                tabstop = value.split(':')[0]
                if tabstop == '0':
                    placeholder = 'cursor'
                else:
                    placeholder = tabstop2placeholders[tabstop]
            return '`%s^' % placeholder

        self.body = re.sub(ultility.placeholder, handle_placeholder, self.body)

