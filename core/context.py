# Imports
import asyncio
import logging
import collections


logger = logging.getLogger('homeghost.' + __name__)



# Class: Context
class Context(object):
    # Init
    def __init__(self):
        self.config = {}
        self.actors = []
        self.commands = collections.deque()
        self.loop = None


    # Queue command
    def queue_command(self, actor, command):
        logger.info('Queing external command %s', actor)
        self.commands.append((actor, command))