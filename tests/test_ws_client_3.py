import asyncio
import json
import uuid
import aiohttp
from websockets.client import connect

SECURE = False
HOST = '0.0.0.0:80'
ACCESS_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjUyZjk4OTJmZDAzZWM4NDk4YTc4OGQyIiwiZXhwIjoxNjk5NDYyMjcwfQ.IJCW8yHHA-qkXRSgtkV69P94uyBz50glicfZQFobFlU"

WS_HOST = f"{'ws' if not SECURE else 'wss'}://{HOST}/v1"

async def main():

    # Start test

    test_id = str(uuid.uuid4())
    print(f'Starting test {test_id}')

    # Connect to the websocket stream
    file_id = '6537955361812bd65c4d72a9'

    async with connect(WS_HOST+f"/file/{file_id}?token="+ACCESS_TOKEN) as websocket:

        counter = 0
        async for rcv in websocket:
            message = json.loads(rcv)
            counter += 1
            print('message ', counter, ':', message)
            
            # On connection, subscribe to file id change stream
            if counter == 1:
                if not message['success']:
                    raise Exception('Wrong message success')
                
                if not message['event'] == 'connection':
                    raise Exception('Wrong message event')
                
                    
            elif counter == 2:
                if not message['success']:
                    raise Exception('Wrong message success')
                
                if not message['event'] == 'subscribed':
                    raise Exception('Wrong message event')

            # On snapshot disconnect

            elif counter == 3:
                if not message['success']:
                    raise Exception('Wrong message success')
                
                if not message['event'] == 'snapshot':
                    raise Exception('Wrong message event')
                
                break
            
            else:
                raise Exception('Unexpected message received')

    print(f'Test {test_id} successfull')

if __name__ == "__main__":
    asyncio.run(main())