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

def format_placeholders(lines):
    """convert ${0} and ${VISUAL} to $0 and $VISUAL"""
    return [line.replace('${0}', '$0').replace('${VISUAL}', '$VISUAL') \
            for line in lines]

