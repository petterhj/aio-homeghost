# Imports
import asyncio
import logging

from tellcore.telldus import TelldusCore, AsyncioCallbackDispatcher
import tellcore.constants as const

from . import AbstractActor


logger = logging.getLogger('homeghost.' + __name__)



# Constants
METHODS = {const.TELLSTICK_TURNON: 'on',
           const.TELLSTICK_TURNOFF: 'off',
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



# Class: TellstickActor
class TellstickActor(AbstractActor):
    # Init
    def __init__(self, config, context):
        super(TellstickActor, self).__init__(config, context)

        self.loop_time = 0.5

        # Callback dispatcher
        # --------------------
        # Dispatcher for use with the event loop available in Python 3.4+.
        # Callbacks will be dispatched on the thread running the event loop. 
        # The loop argument should be a BaseEventLoop instance, e.g. the one 
        # returned from asyncio.get_event_loop().
        dispatcher = AsyncioCallbackDispatcher(self.context.loop)

        # Telldus core
        # --------------------
        # The main class for tellcore-py. Has methods for adding devices and for 
        # enumerating controllers, devices and sensors. Also handles callbacks; 
        # both registration and making sure the callbacks are processed in the 
        # main thread instead of the callback thread.
        self.telldus = TelldusCore(callback_dispatcher=dispatcher)

        # Devices
        # --------------------
        # List of configured devices in /etc/tellstick.conf
        self.devices = self.get_devices()

        # Register event callback handlers
        self.telldus.register_device_event(self.callbacks.device_event)
        self.telldus.register_device_change_event(self.callbacks.device_change_event)
        self.telldus.register_raw_device_event(self.callbacks.raw_event)
        # self.telldus.register_sensor_event(self.sensor_event)
        # self.telldus.register_controller_event(self.controller_event)


    # Loop
    async def loop(self):
        # Super
        await super(TellstickActor, self).loop()

        while self.running:
            # Dispatch all pending callbacks in the current thread.
            self.telldus.callback_dispatcher.process_pending_callbacks()

            await asyncio.sleep(self.loop_time)


    # Get devices
    def get_devices(self):
        ''' Return all known devices. '''

        logger.debug('Fetching list of known devices')

        devices = self.telldus.devices()

        for d in devices:
            logger.debug('> Device: {0}, {1}, {2}, {3}, {4}'.format(d.id, d.name, d.protocol, d.type, d.model))

        return {device.id: device for device in devices}



    # Class: Callbacks
    class Callbacks(AbstractActor.Callbacks):
        # Device event
        def device_event(self, id, method, data, cid):
            logger.debug('Device event, id={}, method={}, data={}, cid={}'.format(
                id, method, data, cid
            ))

            method_string = METHODS.get(method)

            if not method_string:
                logger.warning('Unknown method %s' % (method))
                return

            # string = "[DEVICE] {0} -> {1}".format(id_, method_string)
            # if method == const.TELLSTICK_DIM:
            #     string += " [{0}]".format(data)
            # print(string)

            self.actor.create_event(name='%s.%s' % (
                method_string, self.actor.devices[id].name
            ), payload={
                'method': method_string,
                'id': id,
                'name': self.actor.devices[id].name,
            })

        def device_change_event(self, id, event, type, cid):
            event_string = EVENTS.get(event, "UNKNOWN EVENT {0}".format(event))
            string = "[DEVICE_CHANGE] {0} {1}".format(event_string, id)
            if event == const.TELLSTICK_DEVICE_CHANGED:
                type_string = CHANGES.get(type, "UNKNOWN CHANGE {0}".format(type))
                string += " [{0}]".format(type_string)
            logger.debug(string)

        def raw_event(self, data, controller_id, cid):
            logger.debug('Raw event: {0} <- {1}'.format(controller_id, data))


        '''
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
        '''



    # Class: Actions
    class Actions(AbstractActor.Actions):
        def on(self, device_id):
            device = self.actor.devices.get(device_id)
            if not device:
                return False, 'Unknown device'
            device.turn_on()
            return True, 'Device "%s" turned on' % (device.name)


        def off(self, device_id):
            device = self.actor.devices.get(device_id)
            if not device:
                return False, 'Unknown device'
            device.turn_off()
            return True, 'Device "%s" turned off' % (device.name)


        def dim(self, device_id, level=50):
            if level < 0 or level > 255:
                return False, 'Invalid dim level (%s)' % (str(level))
            device = self.actor.devices.get(device_id)
            if not device:
                return False, 'Unknown device'
            device.dim(level)
            return True, 'Device "%s" dimmed to level %d' % (device.name, level)

        
        # def all_on(self):
        #     for device in self.actor.devices.values():
        #         device.turn_on()
        #     return True, 'All devices (%d) turned on' % (
        #         len(self.actor.devices)
        #     )


        # def all_off(self):
        #     for device in self.actor.devices.values():
        #         device.turn_off()
        #     return True, 'All devices (%d) turned off' % (
        #         len(self.actor.devices)
        #     )