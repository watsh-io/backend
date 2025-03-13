import aiohttp
import asyncio
import uuid

ACCESS_TOKEN = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiNjUyZjk4OTJmZDAzZWM4NDk4YTc4OGQyIiwiZXhwIjoxNjk4OTU5ODQ2fQ.x-1Y19JEeJlGZjaF_HJaC50oo_TLNs0RONuKBeo6Oeg'

async def main() -> None:

    # Start test

    test_id = str(uuid.uuid4())
    print(f'Starting test {test_id}')

    async with aiohttp.ClientSession(
        "http://0.0.0.0:80", 
        headers={'Authorization': f'Bearer {ACCESS_TOKEN}'}
    ) as session:
        
        # Test health
        async with session.get('/v1/health') as response:
            print("Status:", response.status)
            print("Content-type:", response.headers['content-type'])
            html = await response.text()
            print("Body:", html)

        # # Test me
        # async with session.get('/v1/users/me') as response:
        #     print("Status:", response.status)
        #     print("Content-type:", response.headers['content-type'])
        #     html = await response.text()
        #     print("Body:", html)

        # # Create file
        # params = {'slug': test_id, 'description': f'Test {test_id}'}
        # file_data = {"foo": "bar"}
        # async with session.post('/v1/file', params=params, json=file_data) as response:
        #     if not response.status == 201:
        #         raise Exception('File could not be created')
            
        #     response_json = await response.json()
        #     file_id = response_json['id']

        # Get key
        # file_id = '65438cdc835d0109c0011616'
        # key = 'foo'
        # async with session.get(f'/v1/file/{file_id}/key/{key}') as response:
        #     if not response.status == 200:
        #         raise Exception('Key could not be fetched')
            
        #     response_json = await response.json()
        #     print(response_json)

        # Set key
        # file_id = '65438cdc835d0109c0011616'
        # key = 'foo'
        # value = 'baz'
        # params = {
        #     'key': key, 'value': value
        # }
        # async with session.patch(f'/v1/file/{file_id}/key', params=params) as response:
        #     if not response.status == 200:
        #         raise Exception(f'Key could not be set: {response.status}')
            
        #     response_json = await response.json()
        #     print(response_json)
            

if __name__ == '__main__':
    asyncio.run(main())