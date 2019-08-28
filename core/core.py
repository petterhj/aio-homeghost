# Imports
import asyncio
import logging
import functools

from .context import Context
from .http_server import HttpServer
from .socket_server import sio


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

            for actor in self.context.actors:
                self.do_async(actor.stop)
            
            asyncio.wait(self.futures, loop=self.loop)

            self.loop.close()


    # Events processor
    async def events_processor(self):
        while self.running:
            if self.context.events:
                source, name, payload = self.context.events.popleft()

                logger.info('Event received: %s.%s, %s' % (source, name, str(payload)))

                # Actions
                actions = [
                    a for m in self.context.macros if '%s.%s' % (source, name) 
                        in m['events'] for a in m['actions']
                ]

                await self.context.socket_server.emit('event', {
                    'source': source,
                    'name': name,
                    'payload': payload,
                    'actions': len(actions),
                })

                if len(actions) == 0:
                    # logger.info('No actions found for event %s.%s' % (source, name))
                    continue

                logger.info('Executing %d actions for event %s.%s' % (len(actions), source, name))
                
                # Execute actions
                for action in actions:
                    for actor in self.context.actors:
                        if actor.alias == action[0]:
                            self.do_async(actor.execute, action[1], *action[2:])

            await asyncio.sleep(0.01)


    # Results processor
    async def results_processor(self):
        while self.running:
            if self.context.results:
                result = self.context.results.popleft()

                await self.context.socket_server.emit('message', result)

            await asyncio.sleep(0.01)


    # Do async
    def do_async(self, fn, method, *args):
        logger.info('Doing %s%s async via %s' % (method, str(args), str(fn)))
        
        if asyncio.iscoroutinefunction(fn):
            print('ensure_future', '-'*50)
            asyncio.ensure_future(fn(method, *args), loop=self.loop)
        else:
            print('call_soon', '-'*50)
            self.loop.call_soon(functools.partial(fn, method, *args))