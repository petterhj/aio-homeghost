# Imports
import uuid
import time
import logging
import asyncio
import functools


# Logger
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('homeghost.' + __name__)



# Class: Action
class Action:
    # Init
    def __init__(self, actor, method, args):
        self.uuid = str(uuid.uuid4())
        self.context = actor.context

        self.actor = actor
        self.method = method
        self.args = args

        self.created_timestamp = int(time.time())
        self.queued_timestamp = None
        self.completed_timestamp = None
        self.success = None
        self.message = None


    # Wrapper
    def wrapper(self):
        self.success, self.message = self.method(*self.args)
        self.completed_timestamp = int(time.time())
        self.context.results.append(self.dict())


    # Execute
    def execute(self):
        self.queued_timestamp = int(time.time())
        logger.debug('Non-coroutine function, using call_soon')
        self.context.loop.call_soon(self.wrapper)


    # Dict
    def dict(self):
        return {
            'actor': self.actor.alias,
            'method': self.method.__name__,
            'args': self.args,
            'uuid': self.uuid,
            'created_timestamp': self.created_timestamp,
            'queued_timestamp': self.queued_timestamp,
            'completed_timestamp': self.completed_timestamp,
            'success': self.success,
            'message': self.message,
        }


    # Representation
    def __repr__(self):
        return '<%s:%s.%s%r, uuid=%s>' % (
            self.__class__.__name__, self.actor.alias, 
            'self.method', self.args, self.uuid
        )



# Class: AsyncAction
class AsyncAction(Action):
    # Wrapper
    async def wrapper(self):
        self.success, self.message = await self.method(*self.args)
        self.completed_timestamp = time.time()
        self.context.results.append(self.dict())


    # Execute
    def execute(self):
        logger.debug('Coroutine function, using create_task')
        self.context.loop.create_task(self.wrapper())