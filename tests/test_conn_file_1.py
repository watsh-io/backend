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

    
    # Verify that we cannot use the slug twice

    try:
        await conn.file.create(
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
    except exceptions.SlugAlreadyTaken:
        pass
    else:
        raise Exception('Slug used twice')

    # Retrieve the file and version

    snapshot = await conn.file.get(
        client=client,
        user_id=user_id,
        file_id=file_id
    )

    assert snapshot.file == file_id
    assert snapshot.description == description
    assert json.loads(snapshot.data) == data
    assert snapshot.schema_ == schema_id
    
    version = await conn.file.get_version(
        client=client,
        user_id=user_id,
        file_id=file_id,
        version_id=snapshot.version
    )

    assert version.id == snapshot.version
    assert version.file == snapshot.file
    assert version.data == snapshot.data
    assert version.schema_ == snapshot.schema_

    list_descriptions = await conn.file.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 1
    assert list_descriptions[0].file == file_id

    list_version_descriptions = await conn.file.list_version_descriptions(
        client=client,
        user_id=user_id,
        file_id=file_id
    )

    assert len(list_version_descriptions) == 1
    assert list_version_descriptions[0].id == snapshot.version

    # Delete the file

    await conn.file.delete(
        client=client,
        user_id=user_id,
        file_id=file_id
    )

    list_descriptions = await conn.file.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 0

    try:
        await conn.file.list_version_descriptions(
            client=client,
            user_id=user_id,
            file_id=file_id
        )
    except exceptions.NotFound:
        pass
    else:
        raise Exception('File not deleted')
    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )


    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())