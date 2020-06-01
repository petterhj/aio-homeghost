import os
import json
import jinja2
import aiohttp_jinja2
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

        # Setup jinja2 environment
        template_folder = os.path.join(self.context.base_dir, 'templates')
        loader = jinja2.FileSystemLoader(template_folder)

        aiohttp_jinja2.setup(self, **{
            'loader': loader, 
            'trim_blocks': True, 
            'block_start_string': '[%',
            'block_end_string': '%]',
            'variable_start_string': '[[', 
            'variable_end_string': ']]'
        })

        # Actor static files
        # --------------------
        self.actor_static = []

        logger.info('Loading actor static files')

        for actor in self.context.actors:
            file_name = '%s.js' % (actor.name)

            if os.path.isfile(os.path.join(self.context.base_dir, 'actors', file_name)):
                self.actor_static.append(file_name)
                logger.debug('> %s for %s' % (file_name, actor.name))

        logger.info('Found %d actor static files' % (len(self.actor_static)))

        # Routes
        # --------------------
        # Internally routes are served by Application.router (UrlDispatcher 
        # instance). The router is a list of resources, entries in the route 
        # table which corresponds to requested URL.

        self.add_routes([
            web.get('/', self.index),
            web.get('/status/', self.status),
            web.get('/event/{source}/{name}', self.event),
            web.get('/static/actor/{name}.js', self.actor),
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
        server = self.context.loop.create_server(handler, 
            host=config['host'], port=config['port'])

        return server

    
    # Route: Index
    @aiohttp_jinja2.template('index.html')
    async def index(self, request):
        # return web.Response(body=open('static/index.html').read().encode('UTF-8'), content_type='text/html')
        return {
            'actors': []
        }


    # Route: Status
    async def status(self, request):
        return web.Response(**{
            'body': json.dumps(self.context.status).encode('UTF-8'), 
            'headers': {'Content-Type': 'application/json'}
        })


    # Route: Event
    async def event(self, request):
        # Queue event
        self.context.queue_event(**{
            'source': request.match_info['source'], 
            'name': request.match_info['name'],
            'payload': {}
        })

        # Response
        return web.Response(**{
            'body': json.dumps({
                'source': request.match_info['source'],
                'name': request.match_info['name']
            }).encode('UTF-8'), 
            'headers': {'Content-Type': 'application/json'}
        })


    # Route: Actor static
    async def actor(self, request):
        file_name = '%s.js' % (request.match_info['name'])

        if file_name not in self.actor_static:
            logger.error('Could not serve requested file=%s, not found' % (
                file_name
            ))
            raise web.HTTPNotFound()

        return web.FileResponse(os.path.join(self.context.base_dir, 'actors', file_name))