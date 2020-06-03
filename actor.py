# Imports
import re
import os
import json
import inspect
from logger import logger
from dataclasses import dataclass, field


# Class: ActorState
class ActorState:
    # actor: AbstractActor
    running = False
    errors = []

    def __init__(self, actor):
        self.actor = actor

    def __setattr__(self, name, value):
        # current_value = getattr(self, name, None)
        object.__setattr__(self, name, value)

        if name == 'actor' or not self.actor.context.running:
            return
        
        # Notify state updates
        if self.actor in self.actor.context.state_updates:
            logger.warning('State update already queued')
            return

        # print(current_value)
        # print(value)

        # if current_value == value:
        #     logger.error('IGNORING STATE UPDATE, EQUAL')
        #     return

        logger.info('Notifying state update: %s.%s -> %s=%s' % (
            self.actor.name, self.actor.alias, name, str(value)
        ))
        
        self.actor.context.state_updates.append({
            'name': self.actor.name,
            'alias': self.actor.alias,
            'state': {
                'prop': name,
                'value': value
            }
        })

    def to_dict(self):
        asdict = self.__dict__.copy()
        del asdict['actor']
        return asdict



# Class: AbstractActor
class AbstractActor:
    def __init__(self, actor, context):
        logger.info('Initializing %s object, alias=%s' % (
            self.__class__.__name__, actor.get('alias')
        ))
        
        self.context = context
        self.alias = actor.get('alias', self.name)
        self.config = actor.get('config', {})
        self.metadata = actor.get('metadata', {})

        self.state = ActorState(self)

        self.callbacks = self.Callbacks(self)
        self.actions = {
            p[0]: p[1] for p in inspect.getmembers(
                self.Actions(self), predicate=inspect.ismethod
            )
        }

        # Metadata
        # metadata_file = os.path.join(self.context.base_dir, 'actors', self.name, 'meta.json')

        # if os.path.isfile(metadata_file):
        #     try:
        #         with open(metadata_file) as json_file:
        #             metadata = json.load(json_file)
        #     except:
        #         logger.exception('Could not parse actor metadata, name=%s, alias=%s' % (self.name, self.alias))
        #     else:
        #         self.metadata = metadata
        #         logger.debug('Actor metadata loaded, name=%s, alias=%s' % (self.name, self.alias))
        
        # Setup
        try:
            logger.info('Setting up actor')
            self.setup()
        except Exception as e:
            logger.exception(e)
            self.state.errors.append(str(e))
        else:
            self.state.running = True


    # Setup
    def setup(self):
        return


    # Create event
    def create_event(self, name, payload={}):
        ''' Helper method for creating and queuing actor generated events. '''

        # Event
        name = name.lower().replace(' ', '_')
        name = re.sub(r'[^\.\_A-Za-z0-9]+', '', name)
        name = name.replace('__', '_')

        # Queue event
        self.context.queue_event(self.alias.lower(), name, payload)


    # Get method
    def get_method(self, method_name):
        method = self.actions.get(method_name)

        if not method:
            logger.error('Method "%s" not defined for %s' % (
                method_name, self.__class__.__name__
            ))
            
            # Return anonymous method (returning error)
            return lambda: (False, "%s is not implemented" % (method_name))

        return method


    # Properties
    @property
    def name(self):
        return self.__class__.__name__.lower().replace('actor', '')

    @property
    def is_active(self):
        return self.state.running
        # return all(self.state['status'].values())
    


    # Class: Callbacks
    class Callbacks:
        # Init
        def __init__(self, actor):
            self.actor = actor



    # Class: Actions
    class Actions:
        def __init__(self, actor):
            self.actor = actor
