# Imports
import uuid
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

        self.executed = False
        self.success = None
        self.message = None


    # Wrapper
    def wrapper(self):
        self.success, self.message = self.method(*self.args)
        self.executed = True
        self.context.results.append(self.dict())


    # Execute
    def execute(self):
        print('-'*50, 'call_soon', '-'*50)
        # self.context.loop.call_soon(functools.partial(self.method, *self.args))
        self.context.loop.call_soon(self.wrapper)


    # Dict
    def dict(self):
        return {
            'actor': self.actor.alias,
            'method': self.method.__name__,
            'args': self.args,
            'uuid': self.uuid,
            'executed': self.executed,
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
        self.executed = True
        self.context.results.append(self.dict())


    # Execute
    def execute(self):
        print('-'*50, 'create_task', '-'*50)
        # self.context.loop.create_task(self.method(*self.args))
        self.context.loop.create_task(self.wrapper())