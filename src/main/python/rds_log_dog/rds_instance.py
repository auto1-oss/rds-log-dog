from __future__ import print_function, absolute_import, division


class RDSInstance(object):

    def __init__(self, *args, **kwargs):
        self.name = args[0]
        self.engine = kwargs.get('engine', 'mysql')

    def __repr__(self):
        return '%s(%s)' % (self.name, self.engine)
