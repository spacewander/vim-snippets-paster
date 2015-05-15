class Snippet(object):
    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __str__(self):
        return "name: %s\nbody:\n%s\n" % (self.name, self.body)

    __repr__ = __str__
