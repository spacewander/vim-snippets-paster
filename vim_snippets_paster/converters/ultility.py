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

