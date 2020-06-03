# Imports
import os
import logging
import collections
from dataclasses import asdict


logger = logging.getLogger('homeghost.' + __name__)



# Class: Context
class Context(object):
    # Init
    def __init__(self):
        self.base_dir = os.path.dirname(os.path.abspath(__file__))
        self.config = {}
        self.actors = []
        self.events = collections.deque()
        self.results = collections.deque()
        self.state_updates = collections.deque()
        self.backlog = []
        self.http_server = None
        self.socket_server = None
        self.socket_clients = {}
        self.loop = None
        self.running = False


    # Get actor
    def get_actor(self, alias):
        for actor in self.actors:
            if actor.alias == alias:
                return actor
                

    # Queue event
    def queue_event(self, source, name, payload={}, client=None):
        logger.info('Queing %s.%s event for processing' % (source, name))
        self.events.append((source, name, payload, client))


    # Property: Macros
    @property
    def macros(self):
        return self.config.get('macros', [])


    # Property: Status
    @property
    def status(self):
        return {
            'core': {
                'running': self.running,
            },
            'actors': [{
                'name': actor.name,
                'alias': actor.alias,
                'config': actor.config,
                'metadata': actor.metadata,
                'state': actor.state.to_dict(),
                'is_active': actor.is_active,
            } for actor in self.actors],
            'backlog': [dict(e) for e in self.backlog],
            'macros': self.macros,
            'clients': self.socket_clients,
        }
