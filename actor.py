# Imports
import re
import inspect
from logger import logger
# import asyncio



# Class: AbstractActor
class AbstractActor:
    def __init__(self, actor, context):
        logger.info('Initializing %s object, alias=%s' % (
            self.__class__.__name__, actor.get('alias')
        ))
        
        self.context = context
        self.alias = actor.get('alias', self.name)
        self.config = actor.get('config', {})
        # self.public_events = actor.get('events', {})

        self.state = {'running': False}
        # self.web = {'label': '', 'menu': actor.get('web', {}).get('menu', [])}
        self.data = {}

        self.callbacks = self.Callbacks(self)
        self.actions = {
            p[0]:p[1] for p in inspect.getmembers(
                self.Actions(self), predicate=inspect.ismethod)
        }


    # Loop
    async def loop(self):
        ''' Actor loop. '''

        logger.info('Running %s actor loop' % (self.alias))
        self.state['running'] = True


    # Create event
    def create_event(self, name, payload={}):
        ''' Helper method for creating and queuing actor generated events. '''

        # Event
        name = name.lower().replace(' ', '_')
        name = re.sub(r'[^\.\_A-Za-z0-9]+', '', name)
        name = name.replace('__', '_')

        # Queue event
        self.context.queue_event(self.alias.lower(), name, payload)


    # Get method
    def get_method(self, method_name):
        return self.actions[method_name]


    # Stop
    def stop(self):
        logger.info('Stopping actor %s:%s' % (self.__class__.__name__, self.alias))
        self.state['running'] = False

    
    # Properties
    @property
    def name(self):
        return self.__class__.__name__.lower().replace('actor', '')
    
    @property
    def web_label(self):
        return ''

    @property
    def web_menu(self):
        return []



    # Class: Callbacks
    class Callbacks:
        # Init
        def __init__(self, actor):
            self.actor = actor



    # Class: Actions
    class Actions:
        def __init__(self, actor):
            self.actor = actor