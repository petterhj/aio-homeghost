# Imports
import logging


logger = logging.getLogger('homeghost.' + __name__)



# Class: AbstractActor
class AbstractActor(object):
    config = {}
    alias = None
    running = True


    # Loop
    async def loop(self):
        logger.info('Running actor loop')


    # Execute command
    async def execute(self, command):
        logger.info('Executing actor command')


    # Stop
    def stop(self):
        self.running = False