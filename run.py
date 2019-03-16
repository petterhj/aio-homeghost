import asyncio
import logging
import functools

from core import Context
from core.http_server import HttpServer
from actors.tellstick import TellstickActor


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('homeghost.' + __name__)


config = {
    'server': {'host': '0.0.0.0', 'port': 8880},
    'actors': [
        {'class': TellstickActor, 'alias': 'tellstick'}
        # {'actor': KodiActor, 'alias': 'stue', 'host': '192.168.1.4', 'port': 1234}
    ]
}



# Class: Core
class Core(object):
    # Init
    def __init__(self):
        ''' Initialize and configure homeghost core. '''

        logger.info('Initializing...')

        # Context
        self.loop = None
        self.running = False
        self.context = Context()
        self.context.config = config


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

        # Command processor
        self.futures.append(asyncio.ensure_future(self.commands_processor()))

        # Actors
        for actor in self.context.actors:
            self.futures.append(asyncio.ensure_future(actor.loop()))

        try:
            # Server
            server = HttpServer().configure(self.context)
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


    # Command processor
    async def commands_processor(self):
        while self.running:
            if self.context.commands:
                actor_alias, command = self.context.commands.popleft()
                
                for actor in self.context.actors:
                    if actor.alias == actor_alias:
                        self.do_async(actor.execute, command)

            await asyncio.sleep(0.01)


    # Do async
    def do_async(self, fn, *args):
        if asyncio.iscoroutinefunction(fn):
            asyncio.ensure_future(fn(*args), loop=self.loop)
        else:
            self.loop.call_soon(functools.partial(fn, *args))



if __name__ == '__main__':
    Core().run()
