# Imports
import copy
import asyncio

import aioharmony.exceptions as aioexc
from aioharmony.harmonyapi import HarmonyAPI, SendCommandDevice
from aioharmony.harmonyapi import ClientCallbackType

from logger import logger
from actor import AbstractActor



# Class: HarmonyActor
class HarmonyActor(AbstractActor):
    # Init
    def __init__(self, config, context):
        super(HarmonyActor, self).__init__(config, context)
            
        # Properties
        self.client = None
        self.loop_time = 0.5
        self.activities = {}

        # Connect
        self.context.loop.run_until_complete(self.connect())


    # Connect
    async def connect(self):
        # Client
        self.client = HarmonyAPI(self.config.get('host'), loop=self.context.loop)

        # Connect
        try:
            if not await self.client.connect():
                logger.warning('Unable to connect to Harmony HUB, name=%s, fw=%s' % (
                    self.client.name, self.client.fw_version
                ))

                await self.client.close()
        
        except aioexc.TimeOut:
            logger.warning('Harmony HUB connection timed out')

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

        # Config
        self.activities = {
            a['id']: a['label'] for a in self.client.config.get('activity', [])
        }
        self.data['activities'] = self.activities

        logger.info('> Activities:')
        
        for activity_id, activity_name in self.activities.items():
            logger.info('   %s:%s' % (str(activity_id), activity_name))       

        activity_id, activity_name = self.client.current_activity

        self.state['label'] = activity_name

        logger.info('> Current activity, id=%s, name=%s' % (
            str(activity_id), activity_name
        ))


    # @property
    # # Current activity
    # def current_activity(self) -> tuple:
    #     return self._harmony_client.get_activity_name(
    #             self._harmony_client.current_activity_


    
    # Class: Callbacks
    class Callbacks(AbstractActor.Callbacks):
        # New activity
        def new_activity(self, activity_info):
            # Activity
            activity_id, activity_name = activity_info
            
            logger.info('New activity, id=%s, name=%s' % (
                str(activity_id), activity_name
            ))

            # Create event
            self.actor.create_event(name='activity.%s' % (
                activity_name
            ), payload={
                'id': activity_id,
                'name': activity_name,
            })

            self.actor.state['label'] = activity_name


        # New config
        def new_config(self, _=None):
            # Create event
            self.actor.create_event(name='config_updated', payload={
                # 'id': activity_id,
                # 'name': activity_name,
            })


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

        # Start activity
        async def start_activity(self, activity_id):
            try:
                await self.actor.client.start_activity(activity_id)
            
            except aioexc.TimeOut:
                return False, 'Command send timed out' % (
                    command, device_id
                )

            return True, 'Starting activity id=%s, name=%s' % (
                str(activity_id), ''
            )




        # Command
        async def command(self, device_id, command, delay=0):
            try:
                cmd = SendCommandDevice(device_id, command, delay)

                await self.actor.client.send_commands(cmd)
                # self.actor.client.power_off()
            
            except aioexc.TimeOut:
                return False, 'Command send timed out' % (
                    command, device_id
                )
                
            except:
                logger.exception('!!!!!!!'*100)

            return True, 'Command %s sent to device %d' % (
                command, device_id
            )