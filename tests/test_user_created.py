import uuid
import asyncio
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

import src.watsh.connector as conn
import watsh.lib.exceptions as exceptions

MONGO_URI = 'mongodb://localhost:27017/'

"""
Description: Create and delete a user
"""

async def main() -> None:


    client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))

    test_id = str(uuid.uuid4())
    print(f'Starting test {test_id}')

    await conn.setup.indexes(client)
    
    # Create a user
    
    email = f'test-{test_id}@watsh.io'
    current_user_id = await conn.users.create(client=client, email=email)

    # Verify email cannot be used twice

    try:
        await conn.users.create(client=client, email=email)
    except exceptions.EmailAddressAlreadyUsed:
        pass
    else:
        raise Exception('Email address has been used twice')
    
    # Verify wrong email cannot be used

    try:
        wrong_email = 'test@watsh'
        await conn.users.create(client=client, email=wrong_email)
    except exceptions.WrongEmailAddressFormat:
        pass
    else:
        raise Exception('Wrong email address has not been rejected')

    # Get the user by id
    
    user_id = await conn.users.get(client=client, current_user_id=current_user_id)

    assert user_id.id == current_user_id
    assert user_id.email == email

    # Check the sample project

    list_projects = await conn.projects.list_projects(client=client, current_user_id=current_user_id)
    assert len(list_projects) == 1

    for project in list_projects:
        list_environments = await conn.environments.list_environments(
            client=client, 
            current_user_id=current_user_id, 
            project_id=project.id
        )

        assert len(list_environments) == 3

        for environment in list_environments:
            list_branches = await conn.branches.list_branches(
                client=client, 
                current_user_id=current_user_id, 
                project_id=project.id,
                environment_id=environment.id,
            )
            assert len(list_branches) == 1

    # Delete the user
    
    await conn.users.delete(client=client, current_user_id=current_user_id)

    # Verify user is no longer accessible

    try:

        await conn.users.get(client=client, current_user_id=current_user_id)

    except exceptions.UserNotFound:
        pass
    else:
        raise Exception('User found after deletion')

    print(f'Test {test_id} ended successfully')

if __name__ == '__main__':
    asyncio.run(main())