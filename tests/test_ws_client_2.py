import asyncio
import json
import uuid
import aiohttp
from websockets.client import connect, WebSocketClientProtocol

HOST = '0.0.0.0:80'
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjUyZjk4OTJmZDAzZWM4NDk4YTc4OGQyIiwiZXhwIjoxNjk4OTU5ODQ2fQ.x-1Y19JEeJlGZjaF_HJaC50oo_TLNs0RONuKBeo6Oeg"

HTTP_HOST = f"http://{HOST}"
WS_HOST = f"ws://{HOST}/v1"

async def main():

    # Connect to the websocket stream and subscribe to wrong file id

    async with connect(WS_HOST+"?token="+ACCESS_TOKEN) as websocket:
        subscribe = {
            'type': 'subscribe', 
            'file': 'wrongid'
        }

        await websocket.send(json.dumps(subscribe))
        
        async for rcv in websocket:
            message = json.loads(rcv)
            
            if message == {'success': True, 'type': 'connection'}:
                pass
            elif message == {'success': False, 'type': 'error', 'message': 'Wrong id format'}:
                break
            else:
                raise Exception('Unexpected message')
                
           
if __name__ == "__main__":
    asyncio.run(main())