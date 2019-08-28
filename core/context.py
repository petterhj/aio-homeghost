# Imports
import logging
import collections


logger = logging.getLogger('homeghost.' + __name__)



# Class: Context
class Context(object):
    # Init
    def __init__(self):
        self.config = {}
        self.actors = []
        self.events = collections.deque()
        self.results = collections.deque()
        # self.actions = collections.deque()
        self.http_server = None
        self.socket_server = None
        self.loop = None


    # # Queue action
    # def queue_action(self, actor, action, *args, **kwargs):
    #     logger.info('Queing external command %s', actor)
    #     self.actions.append((actor, action, args, kwargs))

    # Queue event
    def queue_event(self, source, name, payload={}):
        # logger.info('Queing %s.%s event for processing' % (source, name))
        self.events.append((source, name, payload))


    # Macros
    @property
    def macros(self):
        return self.config.get('macros', [])
    