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
        self.backlog = []
        # self.actions = collections.deque()
        self.http_server = None
        self.socket_server = None
        self.loop = None


    # Get actor
    def get_actor(self, alias):
        for actor in self.actors:
            if actor.alias == alias:
                return actor
                

    # Queue event
    def queue_event(self, source, name, payload={}):
        logger.info('Queing %s.%s event for processing' % (source, name))
        self.events.append((source, name, payload))


    # Property: Macros
    @property
    def macros(self):
        return self.config.get('macros', [])


    # Property: Status
    @property
    def status(self):
        return {
            # 'config': self.config,
            'actors': [{
                'actor': actor.__class__.__name__,
                'alias': actor.alias,
                'config': actor.config,
                'state': actor.state,
                'events': actor.public_events,
                'data': actor.data
            } for actor in self.actors],
            'backlog': self.backlog,
            'macros': self.macros,
        }
    
    