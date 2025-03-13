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

    # Create a schema
    
    schema_uuid = str(uuid.uuid4())
    slug = schema_uuid
    slug_set = pyobjectid.SET_SLUG
    slug_length = 36
    description = f'Test schema {schema_uuid}'
    description_length = 200
    data = {}
    schema_id = pyobjectid.NULL_OBJECTID
    commit_message = 'First commit.'

    schema_id = await conn.schema.create(
        client=client,
        user_id=user_id,
        slug=slug,
        slug_set=slug_set,
        slug_length=slug_length,
        description=description,
        description_length=description_length,
        data=data,
        commit_message=commit_message
    )

    
    # Verify that we cannot use the slug twice

    try:
        await conn.schema.create(
            client=client,
            user_id=user_id,
            slug=slug,
            slug_set=slug_set,
            slug_length=slug_length,
            description=description,
            description_length=description_length,
            data=data,
            commit_message=commit_message
        )
    except exceptions.SlugAlreadyTaken:
        pass
    else:
        raise Exception('Slug used twice')

    # Retrieve the schema and version

    snapshot = await conn.schema.get(
        client=client,
        user_id=user_id,
        schema_id=schema_id
    )

    assert snapshot.schema_ == schema_id
    assert snapshot.description == description
    assert json.loads(snapshot.data) == data
    
    version = await conn.schema.get_version(
        client=client,
        user_id=user_id,
        schema_id=schema_id,
        version_id=snapshot.version
    )

    assert version.id == snapshot.version
    assert version.data == snapshot.data
    assert version.schema_ == snapshot.schema_

    list_descriptions = await conn.schema.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 1
    assert list_descriptions[0].schema_ == schema_id

    list_version_descriptions = await conn.schema.list_version_descriptions(
        client=client,
        user_id=user_id,
        schema_id=schema_id
    )

    assert len(list_version_descriptions) == 1
    assert list_version_descriptions[0].id == snapshot.version

    # Delete the schema

    await conn.schema.delete(
        client=client,
        user_id=user_id,
        schema_id=schema_id
    )

    list_descriptions = await conn.schema.list_descriptions(
        client=client,
        user_id=user_id
    )
    
    assert len(list_descriptions) == 0

    try:
        await conn.schema.list_version_descriptions(
            client=client,
            user_id=user_id,
            schema_id=schema_id
        )
    except exceptions.NotFound:
        pass
    else:
        raise Exception('Schema not deleted')
    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )

    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())