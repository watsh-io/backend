import uuid
import asyncio
import jsonschema
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

import src.watsh.connector as conn
import watsh.lib.exceptions as exceptions
import watsh.lib.pyobjectid as pyobjectid

MONGO_URI = 'mongodb://localhost:27017/'


json_data = {
  "id": "abc",
  "name": "John Doe",
  "age": 22
}

json_schema = {
    "$schema": "http://json-schema.org/draft-04/schema#",
    "$id": "https://example.com/employee.schema.json",
    "title": "Record of employee",
    "description": "This document records the details of an employee",
    "type": "object",
    "properties": {
        "id": {
            "description": "A unique identifier for an employee",
            "type": "string"
        },
        "name": {
            "description": "full name of the employee",
            "type": "string",
            "minLength": 2
        },
        "age": {
            "description": "age of the employee",
            "type": "number",
            "minimum": 16
        }
    },
    "required": [
        "id",
        "name",
        "age"
    ]
}


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

    slug_set = pyobjectid.SET_SLUG
    slug_length = 36
    description_length = 200
    commit_message = 'First commit.'
    
    schema_uuid = str(uuid.uuid4())
    slug = schema_uuid
    description = f'Test schema {schema_uuid}'
    data = json_schema
    schema_id = pyobjectid.NULL_OBJECTID

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

    # Create a file

    file_uuid_1 = str(uuid.uuid4())
    slug = file_uuid_1
    description = f'Test file {file_uuid_1}'
    data = json_data

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

    # Create a file that does not follow the schema

    file_uuid_2 = str(uuid.uuid4())
    slug = file_uuid_2
    description = f'Test file {file_uuid_2}'
    data = json_data.copy()
    del data['name']

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
    except jsonschema.ValidationError:
        pass
    else:
        raise Exception('File with wrong schema data validated')

    # Delete the schema

    await conn.schema.delete(
        client=client,
        user_id=user_id,
        schema_id=schema_id
    )

    # Create a file with a wrong schema id

    file_uuid_3 = str(uuid.uuid4())
    slug = file_uuid_3
    description = f'Test file {file_uuid_3}'
    data = json_data

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
    except exceptions.NotFound:
        pass
    else:
        raise Exception('File with wrong schema id validated')
    
    # Delete the user

    await conn.users.delete(
        client=client, user_id=user_id
    )

    print(f'Test {test_id} successfull')

if __name__ == '__main__':
    asyncio.run(main())