# Imports
import time
import json
import asyncio
import functools
from loguru import logger

from context import Context
from http_server import HttpServer
from socket_server import SocketServer
from actor import AbstractActor
from action import Event, Action, AsyncAction

import pprint


# Class: Core
class Core(object):
    # Init
    def __init__(self, config):
        ''' Initialize and configure homeghost core. '''

        logger.info('-'*50)
        logger.info('Initializing...')
        logger.debug(config)

        # Context
        self.loop = None
        self.context = Context()
        self.context.config = config


    # Run
    def run(self):
        # Get event loop
        # --------------------
        # Get the current event loop. If there is no current event loop set in 
        # the current OS thread and set_event_loop() has not yet been called, 
        # asyncio will create a new event loop and set it as the current one.
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

        # Message processor
        self.futures.append(asyncio.ensure_future(self.events_processor()))

        try:
            # Servers
            self.context.http_server = HttpServer()
            self.context.socket_server = SocketServer(async_mode='aiohttp')
            self.context.socket_server.configure(self.context)
            
            asyncio.ensure_future(
                self.context.http_server.configure(self.context), 
                loop=self.loop)

            # Startup event
            self.context.queue_event('homeghost', 'startup', payload={})

            # Run the event loop
            logger.info('Running core event loop')
            self.context.running = True
            self.loop.run_forever()


        finally:
            # Stop event loop
            self.context.running = False

            asyncio.wait(self.futures, loop=self.loop)

            self.loop.close()


    # Events processor
    async def events_processor(self):
        while self.context.running:
            # Process events
            if self.context.events:
                # Process event
                source, name, payload, client = self.context.events.popleft()

                logger.info('Event received: %s.%s, %s' % (
                    source, name, str(payload)
                ))

                try:
                    event = Event(self.context, source, name, payload, client)

                except:
                    logger.exception('Could not create event %s.%s' % (
                        source, name
                    ))

                else:
                    # Emit event
                    await self.context.socket_server.emit('event', dict(event))

                    # Add event to backlog
                    self.context.backlog.append(event)

                    # Ignore if no associated actions
                    if len(event.actions) == 0:
                        continue

                    # Execute actions
                    logger.info('Executing %d actions for event %s.%s' % (
                        len(event.actions), source, name
                    ))
                    
                    for action in event.actions:
                        logger.info('- Executing %s%s  on %s' % (
                            action.method.__name__, 
                            action.args,
                            action.actor.alias
                        ))

                        action.execute()

            # Process results
            if self.context.results:
                result = self.context.results.popleft()

                await self.context.socket_server.emit('result', result)

            # Process state updates
            if self.context.state_updates:
                update = self.context.state_updates.popleft()

                await self.context.socket_server.emit('state', update)

            await asyncio.sleep(0.01)


    # Do async
    def do_async(self, method, *args):
        if asyncio.iscoroutinefunction(method):
            logger.debug('Coroutine function, using create_task')
            self.loop.create_task(method(*args))
        else:
            logger.debug('Non-coroutine function, using call_soon')
            self.loop.call_soon(functools.partial(method, *args))