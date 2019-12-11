import os
import json
from aiohttp import web
from loguru import logger



# Class: HTTP Server
class HttpServer(web.Application):
    '''
    Application is a synonym for web-server. Application contains a router 
    instance and a list of callbacks that will be called during application 
    finishing.
    '''

    # Configure
    def configure(self, context):
        # Context
        self.context = context
        config = self.context.config['server']
        
        logger.info('Configuring web server, host={0}, port={1}'.format(
            config['host'], config['port']
        ))

        # Routes
        # --------------------
        # Internally routes are served by Application.router (UrlDispatcher 
        # instance). The router is a list of resources, entries in the route 
        # table which corresponds to requested URL.

        self.add_routes([
            web.get('/', self.index),
            web.get('/status/', self.status),
            web.get('/event/{source}/{name}', self.event),
        ])

        self.router.add_static('/static', './static')


        # Handler
        # --------------------
        # Creates HTTP protocol factory for handling requests.
        handler = self.make_handler()

        # Server
        # --------------------
        # Create a TCP server (socket type SOCK_STREAM) listening on port 
        # of the host address. Returns a Server object.
        server = self.context.loop.create_server(handler, host=config['host'], port=config['port'])

        return server

    
    # Route: Index
    async def index(self, request):
        return web.Response(body=open('static/index.html').read().encode('UTF-8'), content_type='text/html')


    # Route: Status
    async def status(self, request):
        return web.Response(**{
            'body': json.dumps(self.context.status).encode('UTF-8'), 
            'headers': {'Content-Type': 'application/json'}
        })


    # Route: Event
    async def event(self, request):
        
        self.context.queue_event(request.match_info['source'], request.match_info['name'])

        return web.Response(**{
            'body': json.dumps({
                'source': request.match_info['source'],
                'name': request.match_info['name']
            }).encode('UTF-8'), 
            'headers': {'Content-Type': 'application/json'}
        })