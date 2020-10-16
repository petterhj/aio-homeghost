# Imports
import json
import asyncio

import aioharmony.exceptions as aioexc
from aioharmony.harmonyapi import HarmonyAPI, SendCommandDevice
from aioharmony.harmonyapi import ClientCallbackType

from logger import logger
from actor import AbstractActor



# Class: HarmonyActor
class HarmonyActor(AbstractActor):
    # Setup
    def setup(self):
        # Properties
        self.client = None
        self.state.connected = False
        self.activities = {}
        self.devices = {}

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

        self.state.hub = {
            'name': self.client.name,
            'fw': self.client.fw_version,
        }

        # Register callbacks
        self.client.callbacks = ClientCallbackType(
            new_activity=self.callbacks.new_activity,
            config_updated=self.callbacks.new_config,
            connect=self.callbacks.connected,
            disconnect=self.callbacks.disconnected
        )

        # Config
        with open('harmony.txt', 'w') as outfile:
            json.dump(self.client.config, outfile)
        # print(json.dumps(self.client.config))
        
        self.activities = {
            str(a['id']): a['label'] for a in self.client.config.get('activity', [])
        }
        self.state.activities = self.activities

        logger.debug('> Activities:')

        for aid, name in self.activities.items():
            logger.debug('   %s:%s' % (str(aid), name))

        self.devices = {
            str(a['id']): a['label'] for a in self.client.config.get('device', [])
        }
        self.state.devices = self.devices

        logger.debug('> Devices:')
        
        for did, name in self.devices.items():
            logger.debug('   %s:%s' % (str(did), name))   

        # Update current activity
        activity_id, activity_name = self.client.current_activity

        self.state.connected = True
        self.state.current_activity = activity_name

        logger.info('> Current activity, id=%s, name=%s' % (
            str(activity_id), activity_name
        ))


    
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

            self.actor.state.current_activity = activity_name


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
            logger.info("Connected to the HUB: %s" % self.actor.client.name)
            self.actor.state.connected = True
            # self.actor.update_state('connected', True)
            # if not self._available:
            #     # We were disconnected before.
            #     await self.new_config()


        # Disconnected
        async def disconnected(self, _=None):
            """Notification that we're disconnected from the HUB."""
            logger.info('!'*100)
            logger.info("%s: disconnected from the HUB." % self.actor.client.name)
            self.actor.state.connected = False
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
            device_id = str(device_id)

            if device_id not in self.actor.devices:
                return False, 'Unknown device id (%s)' % (device_id)

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

            return True, 'Command %s sent to %s (%s)' % (
                command, self.actor.devices[device_id], device_id
            )