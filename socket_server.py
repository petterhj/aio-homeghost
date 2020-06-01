# Imports
from socketio import AsyncServer
from user_agents import parse as ua_parse
from loguru import logger



# Class: Socket server
class SocketServer(AsyncServer):
    # Configure
    def configure(self, context):
        logger.info('Configuring socket server')

        self.context = context

        # Attach the socket server to the application
        self.attach(self.context.http_server)

        # Register event handlers
        self.on('connect', self.on_connect)
        self.on('disconnect', self.on_disconnect)
        self.on('event', self.on_event)


    # Event: Connect
    async def on_connect(self, sid, environ):
        logger.info('Client connected, sid=%s' % (sid))

        payload = {
            'sid': sid,
            'user_agent': environ.get('HTTP_USER_AGENT'),
            'remote_ip': environ['aiohttp.request'].remote,
            'device': {},
        }

        try:
            user_agent = ua_parse(environ['HTTP_USER_AGENT'])
            payload['device'].update({
                'is_mobile': user_agent.is_mobile,
                'is_tablet': user_agent.is_tablet,
                'is_touch_capable': user_agent.is_touch_capable,
                'is_pc': user_agent.is_pc,
                'is_bot': user_agent.is_bot,
                'os': {
                    'family': user_agent.os.family,
                    'version': user_agent.os.version_string,
                },
                'device': {
                    'family': user_agent.device.family,
                    'brand': user_agent.device.brand,
                    'model': user_agent.device.model,
                },
                'browser': {
                    'family': user_agent.browser.family,
                    'version': user_agent.browser.version_string,
                }
            })
        except:
            pass

        self.context.queue_event('homeghost', 'client.connected', payload=payload)

        print("="*100)
        print(environ)
        print(dir(environ['aiohttp.request']))
        print("="*100)

        await self.emit('status', self.context.status, room=sid)


    # Event: Disconnect
    async def on_disconnect(self, sid):
        logger.info('Client disconnected, sid=%s' % (sid))

        self.context.queue_event('homeghost', 'client.disconnected', payload={
            'sid': sid
        })


    # Event: Event
    async def on_event(self, sid, data):
        source = data.get('source')
        name = data.get('name')

        if not source or not name and 'event' in data:
            event = data['event'].split('.')
            source = event[0]
            name = '.'.join(event[1:])

        self.context.queue_event(source, name)