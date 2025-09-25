import asyncio
import json
import os
from aiohttp import web
import websockets

HOST = '0.0.0.0'
PORT = int(os.getenv('PORT', 8080))

connected_clients = set()

async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    connected_clients.add(ws)
    print("Client connected")

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                # Clients don't send messages, just receive
                pass
            elif msg.type == aiohttp.WSMsgType.ERROR:
                print(f'WebSocket error: {ws.exception()}')
    except Exception as e:
        print(f"WebSocket error: {e}")
    finally:
        connected_clients.remove(ws)
        print("Client disconnected")

    return ws

async def publish_handler(request):
    data = await request.json()
    message = json.dumps(data)

    # Broadcast to all connected clients
    if connected_clients:
        await asyncio.gather(*[client.send_str(message) for client in connected_clients])
        print(f"Broadcasted: {data}")
    else:
        print("No clients connected")

    return web.Response(text="OK")

async def init_app():
    app = web.Application()
    app.router.add_get('/ws/data', websocket_handler)
    app.router.add_post('/publish', publish_handler)
    return app

if __name__ == '__main__':
    app = asyncio.run(init_app())
    web.run_app(app, host=HOST, port=PORT)