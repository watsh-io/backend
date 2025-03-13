import asyncio
import json
from websockets.client import connect

SECURE = True
HOST = 'wss://api.watsh.io'
ACCESS_TOKEN='eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX2lkIjoiNjU5YTc0NWFkNTgxNmNhOTJkNmIyNTU4IiwiZXhwIjoxNzA2ODI4NDAwfQ.fWtXeTmUZA8KLZOHNTbAbjaty4z8_f5YHg5sUOgvJmA'
PROJECT_ID='659a7464d5816ca92d6b2559'
ENVIRONMENT_ID='659a7464d5816ca92d6b255b'
BRANCH_ID='659a7464d5816ca92d6b255c'

WS_HOST = f"{HOST}/v1/{PROJECT_ID}/{ENVIRONMENT_ID}/{BRANCH_ID}"


async def main():

    async with connect(WS_HOST+"?token="+ACCESS_TOKEN) as websocket:

        async for rcv in websocket:
            message = json.loads(rcv)
            print(message)

if __name__ == "__main__":
    asyncio.run(main())