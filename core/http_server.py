import os
import json
import asyncio
import logging

from aiohttp import web

BASE_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
logger = logging.getLogger('homeghost.' + __name__)



# class WebSocket(web.View):
#     async def get(self):
#         ws = web.WebSocketResponse()
#         h = hash(ws)
#         await ws.prepare(self.request)
#         LOG.info('ws client connected, %s clients', len(self.request.app['websockets']) + 1)
#         self.request.app['websockets'][h] = {'ws': ws, 'tag': ''}

#         try:
#             while 1:
#                 msg = await ws.receive_str()
#                 if ';' in msg:
#                     tag, name, cmd = msg.split(';')
#                     self.request.app['websockets'][h]['tag'] = tag
#                     self.request.app.context.item_command(name, cmd)
#                 else:
#                     self.request.app['websockets'][h]['tag'] = msg
#                     LOG.info('got tag %s for %s', msg, h)
#                 LOG.debug('ws msg: %s', msg)
#                 await asyncio.sleep(0.01)
#         finally:
#             if not ws.closed:
#                 try:
#                     await ws.close()
#                 except:
#                     pass
#             del(self.request.app['websockets'][h])



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

        # routes = web.RouteTableDef()
        self.add_routes([
            web.get('/', self.index),
            web.get('/status/', self.status),
        ])


        # self['websockets'] = {}
        # self.router.add_static('/static/', os.path.join(BASE_PATH, 'static'), name='static')
        # self.router.add_route('GET', '/ws', WebSocket, name='chat')
        # self.router.add_route('GET', '/', self.index)

        # Handler
        # --------------------
        # Creates HTTP protocol factory for handling requests.
        handler = self.make_handler()

        # Server
        # --------------------
        # Create a TCP server (socket type SOCK_STREAM) listening on port of the host address.
        # Returns a Server object.
        server = self.context.loop.create_server(handler, host=config['host'], port=config['port'])

        return server

    
    # Route: Index
    async def index(self, request):
        self.context.queue_command('tellstick', 'on')
        return web.Response(body=open('static/index.html').read().encode('UTF-8'), content_type='text/html')


    # Route: Status
    async def status(self, request):
        status = {
            'actors': [actor.alias for actor in self.context.actors]
        }
        headers = {'Content-Type': 'application/json'}
        return web.Response(body=json.dumps(status).encode('UTF-8'), headers=headers)


    
    # def json_resp(self, s):
    #     headers = {'Content-Type': 'application/json'}
    #     return web.Response(body=json.dumps(s).encode('UTF-8'), headers=headers)

    # def resp_404(self, s):
    #     return web.Response(body=s.encode('UTF-8'), status=404)

    # async def on_check(self, item, changed):
    #     s = json.dumps(item.to_dict())
    #     for ws in self['websockets'].values():
    #         if ws['tag'] and ws['tag'] in item.tags:
    #             try:
    #                 await ws['ws'].send_str(s)
    #             except:
    #                 pass