# Imports
import time
import asyncio
import functools
from logger import logger

from context import Context
from http_server import HttpServer
from socket_server import sio
from actor import AbstractActor
from action import Action, AsyncAction



# Class: Core
class Core(object):
    # Init
    def __init__(self, config):
        ''' Initialize and configure homeghost core. '''

        logger.info('-'*50)
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
        self.futures.append(asyncio.ensure_future(self.events_processor()))
        # self.futures.append(asyncio.ensure_future(self.results_processor()))

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

            # Startup event
            self.context.queue_event('homeghost', 'startup', payload={})

            # Run the event loop
            logger.info('Running core event loop')
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
        	# Process events
            if self.context.events:
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

	            # Event
	            event = {
	                'source': source,
	                'name': name,
	                'payload': payload,
	                'actions': [a.dict() for a in actions],
	                'fired_timestamp': int(time.time()),
	            }

	            # Emit event
	            await self.context.socket_server.emit('event', event)

	            self.context.backlog.append(event)

	            if len(actions) == 0:
	                continue

	            logger.info('Executing %d actions for event %s.%s' % (len(actions), source, name))
	            
	            # Execute actions
	            for action in actions:
	                action.execute()

        	# Process results
            if self.context.results:
                result = self.context.results.popleft()

                await self.context.socket_server.emit('result', result)

            await asyncio.sleep(0.01)


    # Results processor
    '''
    async def results_processor(self):
        while self.running:
            # if self.context.results:
            #     result = self.context.results.popleft()

            #     await self.context.socket_server.emit('result', result)
            # pass

            await asyncio.sleep(0.01)
    '''


    # Do async
    def do_async(self, method, *args):
        if asyncio.iscoroutinefunction(method):
            logger.debug('Coroutine function, using create_task')
            self.loop.create_task(method(*args))
        else:
            logger.debug('Non-coroutine function, using call_soon')
            self.loop.call_soon(functools.partial(method, *args))