class Snippet(object):
    """
    This object represents a snippet instance.
    Each type of snippet has its exclusive attributes added during parsing.
    We will distinguish them with a prefix:
        s_ : snipmate
        u_ : ultisnips
        x_ : xptemplate

    """
    def __init__(self, name, body, description):
        self.name = name
        self.body = body
        self.description = description

    def __str__(self):
        # doesn't display exclusive attributes
        return "name: %s\ndescription: %s\nbody:\n%s\n" % (
            self.name, self.description, self.body)

    __repr__ = __str__
