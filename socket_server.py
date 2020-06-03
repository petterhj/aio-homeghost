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

        print("="*100)
        print(environ)
        print(dir(environ['aiohttp.request']))
        print(environ['aiohttp.request'].scheme)
        print("="*100)

        client = {
            'user_agent': environ.get('HTTP_USER_AGENT'),
            'remote_ip': environ['aiohttp.request'].remote,
            'device': {},
        }

        payload = {
            'sid': sid,
            'client': client,
        }

        try:
            user_agent = ua_parse(environ['HTTP_USER_AGENT'])
            client['device'].update({
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
            logger.warning('Could not parse client user agent (ua=%s)' % (
                environ.get('HTTP_USER_AGENT')
            ))

        self.context.socket_clients[sid] = client
        self.context.queue_event('socket', 'client.connected', payload=payload)

        await self.emit('status', self.context.status, room=sid)


    # Event: Disconnect
    async def on_disconnect(self, sid):
        logger.info('Client disconnected, sid=%s' % (sid))

        self.context.queue_event('socket', 'client.disconnected', payload={
            'sid': sid
        })

        del self.context.socket_clients[sid]


    # Event: Event
    async def on_event(self, sid, data):
        try:
            self.context.queue_event(**{
                'source': 'socket', 
                'name': data['name'], 
                'payload': data.get('payload'),
                'client': self.context.socket_clients[sid]['remote_ip'],
            })
        except:
            logger.exception('Failed queing event from socket client')

        """
        source = data.get('source')
        name = data.get('name')

        if not source or not name and 'event' in data:
            event = data['event'].split('.')
            source = event[0]
            name = '.'.join(event[1:])

        self.context.queue_event(source, name)
        """