import re

class NotImplementFeatureException(Exception):
    """an Exception used in parsing"""
    def __init__(self, msg='', feature=None):
        if feature is not None:
            self.message = "%s is not implemented" % feature
        else:
            self.message = msg

    def __str__(self):
        return self.message

class UnsupportFeatureException(Exception):
    """an Exception used in building"""
    def __init__(self, msg='', feature=None):
        if feature is not None:
            self.message = "%s is unsupport" % feature
        else:
            self.message = msg

    def __str__(self):
        return self.message

embeded = re.compile('`(.*?)`', re.MULTILINE | re.DOTALL)

# It is not easy to handle nested brackets with regex in python
# See http://stackoverflow.com/questions/5454322/python-how-to-match-nested-parentheses-with-regex
# Current version can only handle two-level nesting, but it may be enough
placeholder = re.compile('\${([^}]*\$\{[^}]*\}.*?|.*?)}|\$(\d+)(?!\w)', re.MULTILINE | re.DOTALL)
transformation = re.compile('\${(\d+/.*?)}', re.MULTILINE | re.DOTALL)

def format_placeholders(lines):
    """
    1. convert $0 and $VISUAL to ${0} and ${VISUAL}
    2. convert $1, $2, ... into ${1}, ${2}, ...
    """
    return ([
        re.sub('(?<!\\\)\$(\d+)', '${\\1}', line)
        .replace('$VISUAL', '${VISUAL}') for line in lines])

