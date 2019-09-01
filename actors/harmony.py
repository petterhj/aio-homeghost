# Imports
import copy
import asyncio
import logging

import aioharmony.exceptions as aioexc
from aioharmony.harmonyapi import HarmonyAPI, SendCommandDevice
from aioharmony.harmonyapi import ClientCallbackType

from .actor import AbstractActor


logger = logging.getLogger('homeghost.' + __name__)



# Class: HarmonyActor
class HarmonyActor(AbstractActor):
    # Init
    def __init__(self, config, context):
        super(HarmonyActor, self).__init__(config, context)
        
        self.client = None
        self.loop_time = 0.5

        self.context.loop.run_until_complete(self.connect())


    # Connect
    async def connect(self):
        # Client
        self.client = HarmonyAPI(self.config.get('host'))

        # Connect
        if await self.client.connect():
            logger.info('Connected to Harmony HUB, name=%s, fw=%s' % (
                self.client.name, self.client.fw_version
            ))

        # Register callbacks
        self.client.callbacks = ClientCallbackType(
            new_activity=self.callbacks.new_activity,
            config_updated=self.callbacks.new_config,
            connect=self.callbacks.connected,
            disconnect=self.callbacks.disconnected
        )


    # Class: Callbacks
    class Callbacks(AbstractActor.Callbacks):
        # New activity
        def new_activity(self, activity_info: tuple) -> None:
            """Call for updating the current activity."""
            activity_id, activity_name = activity_info
            logger.info('!'*100)
            logger.info("Activity reported as: %s", activity_name)

            self.actor.create_event(name='activity.%s' % (
                activity_name
            ), payload={
                'id': activity_id,
                'name': activity_name,
            })
            # self._current_activity = activity_name
            # self._state = bool(activity_id != -1)
            # self._available = True
            # self.async_schedule_update_ha_state()


        # New config
        async def new_config(self, _=None):
            """Call for updating the current activity."""
            logger.info('!'*100)
            logger.info("Configuration has been updated")
            # self.new_activity(self._client.current_activity)
            # await self.hass.async_add_executor_job(self.write_config_file)


        # Connected
        async def connected(self, _=None):
            """Notification that we're connected to the HUB."""
            logger.info('!'*100)
            logger.info("Connected to the HUB.", self.actor.client.name)
            # if not self._available:
            #     # We were disconnected before.
            #     await self.new_config()


        # Disconnected
        async def disconnected(self, _=None):
            """Notification that we're disconnected from the HUB."""
            logger.info('!'*100)
            logger.info("%s: disconnected from the HUB.", self.actor.client.name)
            # self._available = False
            # We're going to wait for 10 seconds before announcing we're
            # unavailable, this to allow a reconnection to happen.
            await asyncio.sleep(10)

            # if not self._available:
            #     # Still disconnected. Let the state engine know.
            #     self.async_schedule_update_ha_state()


    # Class: Actions
    class Actions(AbstractActor.Actions):
        # async def off(self):
        '''
        def off(self):
            logger.info('%s: Turn off', self.actor.alias)

            try:
                await self.client.power_off()
                # self.actor.client.power_off()
        
            except aioexc.TimeOut:
                logger.exception('%s: Powering off timed-out', self.actor.alias)
                return False, 'Powering off timed-out'
            
            return True, 'Powered off harmony devices'
        '''


        # Send
        async def send(self, device, command, delay=0):
            # logger.info('%s: Turn off', self.actor.alias)

            try:
                cmd = SendCommandDevice(device, command, delay)

                await self.actor.client.send_commands(cmd)
                # self.actor.client.power_off()
            
            except aioexc.TimeOut:
                return self.actor.annouce(False, 'Command send timed out' % (
                    command, device
                ))
                
            except:
                logger.exception('!!!!!!!'*100)

            return True, 'Command %s sent to device %d' % (
                command, device
            )