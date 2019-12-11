# Imports
import re
import inspect
from loguru import logger
# import asyncio



# Class: AbstractActor
class AbstractActor:
    def __init__(self, actor, context):
        logger.info('Initializing %s object, alias=%s' % (
            self.__class__.__name__, actor.get('alias')
        ))
        
        self.context = context
        self.alias = actor.get('alias', self.__class__.__name__)
        self.config = actor.get('config', {})
        self.public_events = actor.get('events', {})
        self.state = {'running': True, 'label': ''}
        self.data = {}

        self.callbacks = self.Callbacks(self)
        self.actions = {
            p[0]:p[1] for p in inspect.getmembers(self.Actions(self), predicate=inspect.ismethod)
        }


    # Loop
    async def loop(self):
        logger.info('Running %s actor loop' % (self.alias))


    # Create event
    def create_event(self, name, payload={}):
        name = name.lower().replace(' ', '_')
        name = re.sub(r'[^\.\_A-Za-z0-9]+', '', name)
        name = name.replace('__', '_')

        self.context.queue_event(self.alias.lower(), name, payload)


    # Get method
    def get_method(self, method_name):
        return self.actions[method_name]


    # Stop
    def stop(self):
        logger.info('Stopping actor %s:%s' % (self.__class__.__name__, self.alias))
        self.state['running'] = False



    # Class: Callbacks
    class Callbacks:
        def __init__(self, actor):
            self.actor = actor



    # Class: Actions
    class Actions:
        def __init__(self, actor):
            self.actor = actor