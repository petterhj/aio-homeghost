# Imports
import re
import logging
import inspect


logger = logging.getLogger('homeghost.' + __name__)



# Class: AbstractActor
class AbstractActor:
    def __init__(self, config, context):
        logger.info('Initializing Tellstick actor object')
        
        self.context = context
        self.config = config
        self.alias = config.get('alias', self.__class__.__name__)
        self.running = True
        # self.actions = self.Actions(self)
        self.callbacks = self.Callbacks(self)
        self.actions = {p[0]:p[1] for p in inspect.getmembers(self.Actions(self), predicate=inspect.ismethod)}


    # Loop
    async def loop(self):
        logger.info('Running %s actor loop' % (self.alias))


    # Execute action
    async def execute(self, action, *args):#, **kwargs):
        if action not in self.actions:
            logger.error('Unknown actor action, %s' % (action))
            return False

        logger.info('Executing %s action, %s' % (self.__class__.__name__, action))

        try:
            result, message = self.actions[action](*args)#, **kwargs)

        except Exception as e:
            logger.exception('Error occured while executing action')
            result, message = False, str(e)

        self.context.results.append({
            'actor': self.alias,
            'action': action,
            'args': args,
            # 'kwargs': kwargs,
            'success': result, 
            'message': message
        })


    # Create event
    def create_event(self, name, payload={}):
        name = name.lower().replace(' ', '_')
        name = re.sub('[^\.A-Za-z0-9]+', '', name)

        self.context.queue_event(self.alias.lower(), name, payload)


    # Stop
    def stop(self):
        self.running = False



    # Class: Callbacks
    class Callbacks:
        def __init__(self, actor):
            self.actor = actor



    # Class: Actions
    class Actions:
        def __init__(self, actor):
            self.actor = actor