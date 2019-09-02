# Imports
import socketio

from logger import logger


# Server
sio = socketio.AsyncServer(async_mode='aiohttp')


# Event
@sio.event
async def event(sid, data):
    # print('-'*50)
    # print(sid)
    # print(data)
    # print('-'*50)
    sio.context.queue_event(data['source'], data['name'])
    
    # await sio.emit('message', {'response': 'my response'})