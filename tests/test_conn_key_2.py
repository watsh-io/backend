import uuid
import asyncio
import json
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

import src.watsh.connector as conn
import watsh.lib.exceptions as exceptions
import watsh.lib.pyobjectid as pyobjectid

MONGO_URI = 'mongodb://localhost:27017/'


async def main() -> None:

    # Connect to database

    client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))

    # Start test

    test_id = str(uuid.uuid4())
    print(f'Starting test {test_id}')

    # Setup indexes

    await conn.setup.indexes(client)

    # Create a user
    
    email = f'test-{test_id}@watsh.io'
    full_name = f'Test {test_id}'
    enabled = True

    user_id = await conn.users.create(
        client=client, email=email, full_name=full_name, enabled=enabled,
    )

    # Create a file (without schema)
    
    file_uuid = str(uuid.uuid4())
    slug = file_uuid
    slug_set = pyobjectid.SET_SLUG
    slug_length = 36
    description = f'Test file {file_uuid}'
    description_length = 200
    data = {
        "foo": [
            {"bar": True},
        ]
    }
    schema_id = pyobjectid.NULL_OBJECTID
    commit_message = 'First commit.'

    file_id = await conn.file.create(
        client=client,
        user_id=user_id,
        slug=slug,
        slug_set=slug_set,
        slug_length=slug_length,
        description=description,
        description_length=description_length,
        data=data,
        schema_id=schema_id,
        commit_message=commit_message
    )

    
    # Get key

    key = "foo"
    separator = "."

    get_key = await conn.file.get_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        separator=separator,
    )

    assert get_key == [{"bar": True}]

    # Get key

    key = "foo.0.bar"
    separator = "."

    get_key = await conn.file.get_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        separator=separator,
    )

    assert get_key == True

    # Set key

    key = "foo.1"
    separator = "."
    value = {"baz": True}
    
    await conn.file.set_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        value=value,
        separator=separator,
        commit_message='',
    )

    get_key = await conn.file.get_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        separator=separator,
    )

    assert get_key == value
    
    # Delete key

    key = "foo.0"
    separator = "."

    await conn.file.delete_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        separator=separator,
        commit_message='',
    )

    get_key = await conn.file.get_key(
        client=client,
        user_id=user_id,
        file_id=file_id,
        key=key,
        separator=separator,
    )
    
    assert get_key == value

    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )


    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())