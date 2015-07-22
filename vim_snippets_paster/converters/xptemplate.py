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
        # raise exception when meeting XSET/XSETm
        # remove repeatition(`...^)
        # handle ComeFirst/ComeLast
        # and remove ...XPT
        for line in input[1:]:
            if line.startswith('XSETm '):
                raise NotImplementFeatureException(feature="XSETm")
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
                    raise NotImplementFeatureException(feature="XSET")
            elif not (line.startswith('...XPT') or
                    line.lstrip().startswith('`...^')):
                body_lines.append(line)
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

        if 'hidden' in self.x_attributes:
            if 'hidden' not in ct:
                ct['hidden'] = {}
            # store the snippet body so that other snippets can include it
            ct['hidden'][snip_name] = body
            self.snippets = []
            return

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
        body = self.remove_repeatition(body)
        self.edge_magic_numer = "Append_this-toedge_value"
        body = self.convert_edge_placeholders(body)
        return self.convert_xptemplate_placeholders(body)

    def remove_repeatition(self, body):
        """
        :help xpt-snippet-repeatition
        replace `...^ with repeated part
        """
        mark = re.compile("`\.\.\.\^(.*?)`\.\.\.\^", re.MULTILINE | re.DOTALL)
        return re.sub(mark, r"\1", body)

    def convert_edge_placeholders(self, body):
        def handle_edge(match):
            groups = match.groups()
            left_edge = groups[0].split(' ')
            for i, v in enumerate(left_edge):
                if v in self.var:
                    left_edge[i] = self.var[v]
            left_edge = " ".join(left_edge)

            right_edge = groups[2].split(' ')
            for i, v in enumerate(right_edge):
                if v in self.var:
                    right_edge[i] = self.var[v]
            right_edge = " ".join(right_edge)

            if len(groups) == 4:
                return r"%s`%s^%s^%s" % (left_edge,
                        self.edge_magic_numer + groups[1],
                        groups[3],
                        right_edge)
            else:
                return r"%s`%s^%s" % (left_edge,
                        self.edge_magic_numer + groups[1],
                        right_edge)

        def handle_left_only_edge(match):
            groups = match.groups()
            left_edge = groups[0].split(' ')
            for i, v in enumerate(left_edge):
                if v in self.var:
                    left_edge[i] = self.var[v]
            left_edge = " ".join(left_edge)

            if len(groups) == 3:
                return r"%s`%s^%s^" % (left_edge,
                        self.edge_magic_numer + groups[1],
                        groups[2])
            else:
                return r"%s`%s^" % (left_edge,
                        self.edge_magic_numer + groups[1])

        edge_with_placeholder = re.compile(
                '`([^^`]*)`([^^`]*)`([^^]*)\^([^^`]*)\^')
        r = re.sub(edge_with_placeholder, handle_edge, body)
        edge = re.compile('`([^^`]*)`([^^`]*)`([^^]*)\^')
        r = re.sub(edge, handle_edge, r)

        left_only_edge_with_placeholder = re.compile(
                '`([^^`]*)`([^^]*)\^([^^`]*)\^')
        r = re.sub(left_only_edge_with_placeholder, handle_left_only_edge, r)
        left_only_edge = re.compile('`([^^`]*)`([^^`]*)\^')
        return re.sub(left_only_edge, handle_left_only_edge, r)

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

        # Handle include value
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
        self.order_counters[value] = self.order_counters.setdefault(value, 0) + 1
        if should_set_edge:
            self.edge[value] = self.order_counters[value]

        # Update self.value so that we can use it in next parser
        if value not in self.values:
            self.order += 1
            self.values[value] = self.order
        if placeholder != '':
            return "`%s^%s^" % (value, placeholder)
        else:
            return "`%s^" % value

    def escape(self, placeholder):
        """escape special characters like $ and {, }"""
        return placeholder.replace('$', '\$').replace('{', '\{').replace('}', '\}')

    def convert_value(self, match):
        """
        :match is a MatchObject contains the value inside `^
        """
        # match.group(1) may be 'value^placeholder' or 'value'
        value, _, placeholder = match.group(1).partition('^')
        if value in self.order_counters:
            self.order_counters[value] -= 1
            if self.order_counters[value] == 0:
                order = self.values[value]
                if placeholder != '':
                    return "${%d:%s}" % (order, self.escape(placeholder))
                return "${%d:%s}" % (order, self.escape(value))
            else:
                return "$%d" % self.values[value]
        else:
            order = self.values[value]
            if placeholder != '':
                return "${%d:%s}" % (order, self.escape(placeholder))
            return "${%d:%s}" % (order, self.escape(value))

    def convert_xptemplate_placeholders(self, body):
        """
        convert the xptemplate style placeholder(`value^placeholder^) to
        snipmate-like one(${order:placeholder})
        """
        self.order_counters = {}
        self.edge = {}

        placeholder_pattern = re.compile('`([^^`]+\^?[^^`]*)\^')
        r = re.sub(placeholder_pattern, self.convert_placeholder, body)
        for value in self.values:
            order = self.values[value]
            if order < 0: # value in ComeLast
                self.values[value] = self.order - order
        # placeholder with edge should be the first, so reset counter here
        for value in self.order_counters:
            if value not in self.edge:
                self.order_counters[value] = 1
            else:
                self.order_counters[value] = self.edge[value]
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
        print(snippet.body)
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
        """
        iterate each tabstop and convert it to xptemplate style placeholder
        """
        # since transformation is not implemented, there are seven cases:
        # 0. $1
        # 1. ${1}
        # 2. ${1:some}
        # 3. ${VISUAL}
        # 4. ${VISUAL:some}
        # 5. ${0}
        # 6. ${0:some}
        order = 1
        self.unorder = False
        self.tabstop_to_placeholder = {}
        self.tabstop_counters = {}
        self.should_have_edge = set()
        self.mirrors = set()
        for match in re.finditer(ultility.placeholder, self.body):
            placeholder = match.group(1)
            if placeholder is None: # case 0
                placeholder = match.group(2)
            if placeholder.startswith('VISUAL') or placeholder.startswith('0'):
                continue
            tabstop_order = placeholder
            if placeholder.isdigit():
                self.mirrors.add(placeholder)
            else:
                tabstop_order, text = placeholder.split(':', 2)
                if re.search(ultility.placeholder, text) is not None:
                    raise UnsupportFeatureException(
                            "xptemplate doesn't support nested placeholder")
                self.tabstop_to_placeholder[tabstop_order] = text
                if tabstop_order in self.mirrors: # $digit met
                    self.should_have_edge.add(tabstop_order)

            if not self.unorder:
                if order <= int(tabstop_order) <= order + 1: # 1 1 2 3 ...
                    order = int(tabstop_order)
                else:
                    self.unorder = True

        # counter will be used inside function handle_placeholder
        self.counter = 'h' # for tabstop like ${1}, which doesn't have a default value
        self.body = re.sub(ultility.placeholder, self.handle_placeholder, self.body)
        if self.unorder:
            orders = [v for k, v in
                    sorted(self.tabstop_to_placeholder.items(), key=lambda x:x[0])]
            come_first = "XSET ComeFirst=%s\n" % " ".join(orders)
            self.body = come_first + self.body

    def escape(self, placeholder):
        """escape special characters like ` and ^"""
        return placeholder.replace('`', '\`').replace('^', '\^')

    def handle_placeholder(self, match):
        """
        used in convertion from tabstop to xptemplate style placeholder

        :match is a MatchObject contains tabstop value,
        if the tabstop is sth like $digit, the value is stored in group 2,
        otherwise the value is stored in group 1
        """
        value = match.group(1)
        if value is None:
            value = match.group(2)
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
            elif value in self.tabstop_to_placeholder:
                placeholder = self.tabstop_to_placeholder[value]
            else:
                if self.unorder:
                    # add prefix make it safer, but dirty
                    self.counter = chr(ord(self.counter) + 1)
                    placeholder = self.tabstop_to_placeholder.setdefault(
                            value, self.counter)
                # if placeholders are in order(no need to use ComeFirst), keep anonymous
                else:
                    placeholder = ''
        else:
            tabstop = value.split(':')[0]
            if tabstop == '0':
                placeholder = 'cursor'
            else:
                placeholder = self.tabstop_to_placeholder[tabstop]
                if tabstop in self.should_have_edge:
                    return '``%s^' % self.escape(placeholder)
        return '`%s^' % self.escape(placeholder)

