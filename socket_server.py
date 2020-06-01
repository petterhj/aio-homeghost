# Imports
from socketio import AsyncServer
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
        self.on('event', self.on_event)


    # Event: Connect
    async def on_connect(self, sid, environ):
        logger.info('Client connected, sid=%s' % (sid))

        self.context.queue_event('homeghost', 'client.connected', payload={
            'sid': sid
        })

        await self.emit('status', self.context.status, room=sid)


    # Event: Event
    async def on_event(self, sid, data):
        source = data.get('source')
        name = data.get('name')

        if not source or not name and 'event' in data:
            event = data['event'].split('.')
            source = event[0]
            name = '.'.join(event[1:])

        self.context.queue_event(source, name)