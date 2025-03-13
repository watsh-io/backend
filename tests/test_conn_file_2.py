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
    
    slug_length = 36
    slug_set = pyobjectid.SET_SLUG
    description_length = 200
    data = {}
    commit_message = 'First commit.'
    
    file_uuid_1 = str(uuid.uuid4())
    slug = file_uuid_1
    description = f'Test file {file_uuid_1}'
    schema_id = pyobjectid.NULL_OBJECTID

    file_id_1 = await conn.file.create(
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

    
    # Change its slug

    new_file_uuid_1 = str(uuid.uuid4())

    await conn.file.slug_update(
        client=client,
        user_id=user_id,
        file_id=file_id_1,
        slug=new_file_uuid_1,
        slug_set=slug_set,
        slug_length=slug_length,
    )

    # Change its description
    
    new_description = f'Test file {new_file_uuid_1}'

    await conn.file.description_update(
        client=client,
        user_id=user_id,
        file_id=file_id_1,
        description=new_description,
        description_length=description_length,
    )


    # Verify

    snapshot = await conn.file.get(
        client=client,
        user_id=user_id,
        file_id=file_id_1
    )

    assert snapshot.slug == new_file_uuid_1
    assert snapshot.description == new_description

    # Create a second file

    file_uuid_2 = str(uuid.uuid4())
    slug = file_uuid_2
    description = f'Test file {file_uuid_2}'
    schema_id = pyobjectid.NULL_OBJECTID

    file_id_2 = await conn.file.create(
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

    
    # Verify that we cannot change the slug to file 1 slug

    try:
        await conn.file.slug_update(
            client=client,
            user_id=user_id,
            file_id=file_id_2,
            slug=new_file_uuid_1,
            slug_set=slug_set,
            slug_length=slug_length,
        )
    except exceptions.SlugAlreadyTaken:
        pass
    else:
        raise Exception('Slug used twice')

    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )


    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())