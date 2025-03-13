import uuid
import asyncio
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

    # Create a file

    file_id = str(uuid.uuid4())
    slug = file_id
    slug_set = pyobjectid.SET_SLUG
    slug_length = 36
    description = f'Test file {file_id}'
    description_length = 200
    data = {}
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

    # TODO: Create a schema

    # Delete the user
    
    await conn.users.delete(
        client=client, user_id=user_id
    )

    # Verify the file and schema are deleted
    list_descriptions = await conn.file.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 0

    list_descriptions = await conn.schema.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 0

    # Verify the user is deleted

    try:

        await conn.users.get(
            client=client, user_id=user_id
        )

        await conn.users.get_by_email(
            client=client, email=email
        )

    except exceptions.UserNotFound:
        pass
    else:
        raise Exception('User found after deletion')

    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())