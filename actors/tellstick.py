# Imports
import asyncio
import logging

from tellcore.telldus import TelldusCore, AsyncioCallbackDispatcher
import tellcore.constants as const

from . import AbstractActor


logger = logging.getLogger('homeghost.' + __name__)



# Constants
METHODS = {const.TELLSTICK_TURNON: 'turn on',
           const.TELLSTICK_TURNOFF: 'turn off',
           const.TELLSTICK_BELL: 'bell',
           const.TELLSTICK_TOGGLE: 'toggle',
           const.TELLSTICK_DIM: 'dim',
           const.TELLSTICK_LEARN: 'learn',
           const.TELLSTICK_EXECUTE: 'execute',
           const.TELLSTICK_UP: 'up',
           const.TELLSTICK_DOWN: 'down',
           const.TELLSTICK_STOP: 'stop'}

EVENTS = {const.TELLSTICK_DEVICE_ADDED: "added",
          const.TELLSTICK_DEVICE_REMOVED: "removed",
          const.TELLSTICK_DEVICE_CHANGED: "changed",
          const.TELLSTICK_DEVICE_STATE_CHANGED: "state changed"}

CHANGES = {const.TELLSTICK_CHANGE_NAME: "name",
           const.TELLSTICK_CHANGE_PROTOCOL: "protocol",
           const.TELLSTICK_CHANGE_MODEL: "model",
           const.TELLSTICK_CHANGE_METHOD: "method",
           const.TELLSTICK_CHANGE_AVAILABLE: "available",
           const.TELLSTICK_CHANGE_FIRMWARE: "firmware"}

TYPES = {const.TELLSTICK_CONTROLLER_TELLSTICK: 'tellstick',
         const.TELLSTICK_CONTROLLER_TELLSTICK_DUO: "tellstick duo",
         const.TELLSTICK_CONTROLLER_TELLSTICK_NET: "tellstick net"}



# Class: Tellstick
class Tellstick(object):
    # Init
    def __init__(self, loop):
        '''
        Initialize the Tellstick object.
        '''

        # Callback dispatcher
        # --------------------
        # Dispatcher for use with the event loop available in Python 3.4+.
        # Callbacks will be dispatched on the thread running the event loop. 
        # The loop argument should be a BaseEventLoop instance, e.g. the one 
        # returned from asyncio.get_event_loop().
        dispatcher = AsyncioCallbackDispatcher(loop)

        # Telldus core
        # --------------------
        # The main class for tellcore-py. Has methods for adding devices and for 
        # enumerating controllers, devices and sensors. Also handles callbacks; 
        # both registration and making sure the callbacks are processed in the 
        # main thread instead of the callback thread.
        self.telldus = TelldusCore(callback_dispatcher=dispatcher)


    # Get devices
    def get_devices(self):
        ''' Return all known devices. '''

        logger.debug('Fetching list of known devices')

        devices = self.telldus.devices()
        for d in devices:
            print(d)
        return {device.id: device for device in devices}

    
    # On
    def on(self, device):
        device.turn_on()


    # Event callback handlers
    def device_event(self, id_, method, data, cid):
        method_string = METHODS.get(method, "UNKNOWN METHOD {0}".format(method))
        string = "[DEVICE] {0} -> {1}".format(id_, method_string)
        if method == const.TELLSTICK_DIM:
            string += " [{0}]".format(data)
        print(string)


    def device_change_event(self, id_, event, type_, cid):
        event_string = EVENTS.get(event, "UNKNOWN EVENT {0}".format(event))
        string = "[DEVICE_CHANGE] {0} {1}".format(event_string, id_)
        if event == const.TELLSTICK_DEVICE_CHANGED:
            type_string = CHANGES.get(type_, "UNKNOWN CHANGE {0}".format(type_))
            string += " [{0}]".format(type_string)
        print(string)


    def raw_event(self, data, controller_id, cid):
        logger.debug('Raw event: {0} <- {1}'.format(controller_id, data))


    def sensor_event(self, protocol, model, id_, dataType, value, timestamp, cid):
        logger.debug('Sensor event: [SENSOR] {0} [{1}/{2}] ({3}) @ {4} <- {5}'.format(
            id_, protocol, model, dataType, timestamp, value
        ))


    def controller_event(self, id_, event, type_, new_value, cid):
        event_string = EVENTS.get(event, "UNKNOWN EVENT {0}".format(event))
        string = "[CONTROLLER] {0} {1}".format(event_string, id_)
        if event == const.TELLSTICK_DEVICE_ADDED:
            type_string = TYPES.get(type_, "UNKNOWN TYPE {0}".format(type_))
            string += " {0}".format(type_string)
        elif (event == const.TELLSTICK_DEVICE_CHANGED
              or event == const.TELLSTICK_DEVICE_STATE_CHANGED):
            type_string = CHANGES.get(type_, "UNKNOWN CHANGE {0}".format(type_))
            string += " [{0}] -> {1}".format(type_string, new_value)
        print(string)


    # Listen
    async def listen(self):
        # Register event callback handlers
        self.telldus.register_device_event(self.device_event)
        self.telldus.register_device_change_event(self.device_change_event)
        self.telldus.register_raw_device_event(self.raw_event)
        self.telldus.register_sensor_event(self.sensor_event)
        self.telldus.register_controller_event(self.controller_event)

        # Dispatch all pending callbacks in the current thread.
        self.telldus.callback_dispatcher.process_pending_callbacks()



# Class: TellstickActor
class TellstickActor(AbstractActor):
    # Init
    def __init__(self, config, context):
        logger.info('Initializing Tellstick actor object')

        self.config = config
        self.alias = config.get('alias')
        self.tellstick = Tellstick(context.loop)
        self.loop_time = 0.5


    # Loop
    async def loop(self):
        # Super
        await super(TellstickActor, self).loop()

        while self.running:
            # print('test')
            # dev = await self.telldus.get_devices()
            # print(dev)
            await self.tellstick.listen()   

            await asyncio.sleep(self.loop_time)


    # Execute command
    async def execute(self, command):
        # Supper
        await super(TellstickActor, self).execute(command)
            
        # Commands
        if command == 'devices':
            self.tellstick.get_devices()

        if command == 'on':
            for device_id, device in self.tellstick.get_devices().items():
                if device_id == 200:
                    self.tellstick.on(device)