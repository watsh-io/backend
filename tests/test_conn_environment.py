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

    # Create an environment
    
    env_uuid = str(uuid.uuid4())
    slug = env_uuid
    slug_set = pyobjectid.SET_SLUG
    slug_length = 36
    description = f'Test env {env_uuid}'
    description_length = 200

    environment_id = await conn.environments.create(
        client=client,
        user_id=user_id,
        slug=slug,
        slug_set=slug_set,
        slug_length=slug_length,
        description=description,
        description_length=description_length,
    )

    
    # Verify that we cannot use the slug twice

    try:
        await conn.environments.create(
            client=client,
            user_id=user_id,
            slug=slug,
            slug_set=slug_set,
            slug_length=slug_length,
            description=description,
            description_length=description_length,
        )
    except exceptions.SlugAlreadyTaken:
        pass
    else:
        raise Exception('Slug used twice')

    # Retrieve the schema and version

    env = await conn.environments.get(
        client=client,
        user_id=user_id,
        environment_id=environment_id
    )

    assert env.id == environment_id
    assert env.slug == slug
    assert env.description == description
    
    # List vaults
    env_list = await conn.environments.list_environments(
        client=client,
        user_id=user_id
    )

    assert len(env_list) == 1
    assert env_list[0].id == environment_id
    assert env_list[0].slug == slug
    assert env_list[0].description == description

    # Slug update
    new_slug = 'new-slug'
    await conn.environments.slug_update(
        client=client,
        user_id=user_id,
        environment_id=environment_id,
        slug=new_slug,
        slug_set=slug_set,
        slug_length=slug_length
    )

    env = await conn.environments.get(
        client=client,
        user_id=user_id,
        environment_id=environment_id
    )

    assert env.id == environment_id
    assert env.slug == new_slug
    assert env.description == description

    # Description update
    new_description = 'new-description'
    await conn.environments.description_update(
        client=client,
        user_id=user_id,
        environment_id=environment_id,
        description=new_description,
        description_length=description_length
    )

    env = await conn.environments.get(
        client=client,
        user_id=user_id,
        environment_id=environment_id
    )

    assert env.id == environment_id
    assert env.slug == new_slug
    assert env.description == new_description

    # Delete the schema

    await conn.environments.delete(
        client=client,
        user_id=user_id,
        environment_id=environment_id
    )

    env_list = await conn.vault.list_vaults(
        client=client,
        user_id=user_id
    )

    assert len(env_list) == 0
    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )

    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())