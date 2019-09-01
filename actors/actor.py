# Imports
import re
import logging
import inspect
import asyncio


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


    # # Annouce result
    # def annouce(self, result, message):
    #     self.context.results.append({
    #         'actor': self.alias,
    #         # 'action': action,
    #         # 'args': args,
    #         # 'kwargs': kwargs,
    #         'success': result, 
    #         'message': message
    #     })


    '''
    # Execute action
    def execute(self, action, *args):#, **kwargs):
        if action not in self.actions:
            logger.error('Unknown actor action, %s' % (action))
            return False

        logger.info('Executing %s action, %s' % (self.__class__.__name__, action))

        print(action)
        print(args)
        print('!'*100)
        try:
            # result, message = self.actions[action](*args)#, **kwargs)
            # self.actions[action](*args)#, **kwargs)
            # self.actions[action](*args)#, **kwargs)
            result = True
            message = 'foo'

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
    '''


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
        self.running = False



    # Class: Callbacks
    class Callbacks:
        def __init__(self, actor):
            self.actor = actor



    # Class: Actions
    class Actions:
        def __init__(self, actor):
            self.actor = actor