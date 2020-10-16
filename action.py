# Imports
import re
import uuid
import time
import asyncio

from logger import logger
from context import Context
from actor import AbstractActor


class Message:
    class Serializer:
        pass

    # Encode
    def encode(self, value):
        if isinstance(value, Context):
            return id(value)
        if isinstance(value, AbstractActor):
            return value.alias
        if isinstance(value, Message):
            return dict(value)
        else:
            return value

    # Iter
    def __iter__(self):
        properties = self.__dict__
        exclude = getattr(self.Serializer, 'exclude_attrs', [])

        for attr in exclude:
            if attr in properties.keys():
                print('- x', attr)
                del properties[attr]

        for attr, value in properties.items():
            if callable(value):
                yield (attr, value.__name__)
            elif isinstance(value, list):
                yield (attr, [self.encode(e) for e in value])
            else:
                yield (attr, self.encode(value))


# Class: Event
class Event(Message):
    class Serializer:
        exclude_attrs = []

    # Init
    def __init__(self, context, source, name, payload={}, client=None):
        self.context = context
        self.uuid = str(uuid.uuid4())

        self.source = source
        self.name = name
        self.payload = payload
        self.client = client

        self.created_timestamp = int(time.time())

        self.actions = self.get_actions()

    # Get actions
    def get_actions(self):
        ''' Return list of actions associated with event. '''

        # Actions
        actions = []

        logger.debug('Getting actions for event %s.%s (%d macros total)' % (
            self.source, self.name, len(self.context.macros)
        ))

        for action in [
            a for m in self.context.macros if '%s.%s' % (self.source, self.name) 
                in m['events'] for a in m['actions']]:

            actor = self.context.get_actor(action[0])
            method = actor.get_method(action[1])

            args = self.inject_payload(action[2:])
            is_coroutine = asyncio.iscoroutinefunction(method)
            action_type = AsyncAction if is_coroutine else Action

            logger.debug('- Action: %s%s through %s' % (
                method.__name__, args, actor.alias
            ))

            actions.append(action_type(actor, method, args))

        logger.debug('Found %d actions' % (len(actions)))

        return actions

    # Inject event payload
    def inject_payload(self, args):
        processed_args = []

        for arg in args:
            match = re.match(r'^\{\{([A-Za-z0-9]+)\}\}$', str(arg))
            if match:
                processed_args.append(self.payload[match.group(1)])
                logger.debug("Injecting event payload: %s = %s" % (arg, self.payload[match.group(1)]))
            else:
                processed_args.append(arg)

        return processed_args



# Class: Action
class Action(Message):
    class Serializer:
        exclude_attrs = []

    # Init
    def __init__(self, actor, method, args):
        self.context = actor.context
        self.uuid = str(uuid.uuid4())

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
        self.context.results.append(dict(self))


    # Execute
    def execute(self):
        logger.debug('Non-coroutine function, using call_soon')
        self.queued_timestamp = int(time.time())
        self.context.loop.call_soon(self.wrapper)


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
        self.completed_timestamp = int(time.time())
        self.context.results.append(dict(self))


    # Execute
    def execute(self):
        logger.debug('Coroutine function, using create_task')
        self.queued_timestamp = int(time.time())
        self.context.loop.create_task(self.wrapper())