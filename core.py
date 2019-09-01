# Imports
import asyncio
import logging
import functools

from context import Context
from http_server import HttpServer
from socket_server import sio
from action import Action, AsyncAction


# Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('homeghost.' + __name__)



# Class: Core
class Core(object):
    # Init
    def __init__(self, config):
        ''' Initialize and configure homeghost core. '''

        logger.info('Initializing...')

        # Context
        self.loop = None
        self.running = False
        self.context = Context()
        self.context.config = config
        self.context.socket_server = sio


    # Run
    def run(self):
        # Get current event loop 
        self.loop = asyncio.get_event_loop()
        self.context.loop = self.loop
        self.futures = []

        # Register actor instances
        logger.info('Registering {0} actor instances'.format(
            len(self.context.config['actors'])
        ))

        self.context.actors = list(map(
            lambda a: a['class'](a, self.context), self.context.config['actors']
        ))

        # Actions processor
        # self.futures.append(asyncio.ensure_future(self.actions_processor()))
        self.futures.append(asyncio.ensure_future(self.events_processor()))
        self.futures.append(asyncio.ensure_future(self.results_processor()))

        # Actors
        for actor in self.context.actors:
            self.futures.append(asyncio.ensure_future(actor.loop()))

        try:
            # Server
            self.context.http_server = HttpServer()
            self.context.socket_server.context = self.context
            self.context.socket_server.attach(self.context.http_server)
            server = self.context.http_server.configure(self.context)
            asyncio.ensure_future(server, loop=self.loop)

            # Run the event loop
            self.running = True
            self.loop.run_forever()

        finally:
            # Stop event loop
            self.running = False

            # for actor in self.context.actors:
            #     self.do_async(actor.stop)
            
            asyncio.wait(self.futures, loop=self.loop)

            self.loop.close()


    # Events processor
    async def events_processor(self):
        while self.running:
            if not self.context.events:
                await asyncio.sleep(0.01)
                continue

            # Process event
            source, name, payload = self.context.events.popleft()

            logger.info('Event received: %s.%s, %s' % (source, name, str(payload)))

            # Actions
            actions = []

            for action in [
                a for m in self.context.macros if '%s.%s' % (source, name) 
                    in m['events'] for a in m['actions']]:

                actor = self.context.get_actor(action[0])
                method = actor.get_method(action[1])
                args = action[2:]
                action_type = AsyncAction if asyncio.iscoroutinefunction(method) else Action

                actions.append(action_type(actor, method, args))

            # Emit event
            await self.context.socket_server.emit('event', {
                'source': source,
                'name': name,
                'payload': payload,
                'actions': [a.dict() for a in actions],
            })

            if len(actions) == 0:
                continue

            logger.info('Executing %d actions for event %s.%s' % (len(actions), source, name))
            
            # Execute actions
            for action in actions:
                action.execute()


    # Results processor
    async def results_processor(self):
        while self.running:
            if self.context.results:
                result = self.context.results.popleft()

                await self.context.socket_server.emit('result', result)

            await asyncio.sleep(0.01)


    # Do async
    def do_async(self, method, *args):
        if asyncio.iscoroutinefunction(method):
            print('-'*50, 'create_task', '-'*50)
            print(method)
            self.loop.create_task(method(*args))
        else:
            print('-'*50, 'call_soon', '-'*50)
            self.loop.call_soon(functools.partial(method, *args))