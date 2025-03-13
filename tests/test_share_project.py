import uuid
import asyncio
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

import src.watsh.connector as conn
import watsh.lib.exceptions as exceptions
from watsh.lib.pyobjectid import SET_SLUG

MONGO_URI = 'mongodb://localhost:27017/'

"""
Description: Create a project and share it with another user
"""

async def main() -> None:

    client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))

    test_id = str(uuid.uuid4())
    print(f'Starting test {test_id}')

    await conn.setup.indexes(client)
    
    # Create a user
    
    email = f'test-{test_id}@watsh.io'
    current_user_id = await conn.users.create(client=client, email=email)

    # Create invited user
    
    invited_email = f'invite-{test_id}@watsh.io'
    invited_user_id = await conn.users.create(client=client, email=invited_email)

    # Get first user project

    list_projects = await conn.projects.list_projects(client=client, current_user_id=current_user_id)
    project_id = list_projects[0].id
    
    # Check the invited user has no access to first user projects
    
    invited_list_projects = await conn.projects.list_projects(client=client, current_user_id=invited_user_id)
    for invited_project in invited_list_projects:
        assert invited_project.id != project_id
    
    # Share the sample project

    await conn.members.create(
        client=client, 
        current_user_id=current_user_id,
        invited_user_id=invited_user_id,
        project_id=project_id
    )

    # Now, check the invited user has access to first user projects
    
    invited_list_projects = await conn.projects.list_projects(client=client, current_user_id=invited_user_id)
    access = False
    for invited_project in invited_list_projects:
        if invited_project.id == project_id:
            access = True
    
    assert access == True

    # Try to remove owner

    try:
        await conn.members.delete(
            client=client,
            current_user_id=invited_user_id,
            invited_user_id=current_user_id,
            project_id=project_id
        )
    except exceptions.OwnerCannotBeDeleted:
        pass
    else:
        raise Exception('Owner has been deleted from project')
    
    # Rename project

    await conn.projects.slug_update(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        slug='sample-2',
        slug_set=SET_SLUG,
        slug_length=20,
    )

    await conn.projects.slug_update(
        client=client,
        current_user_id=invited_user_id,
        project_id=project_id,
        slug='sample-2-2',
        slug_set=SET_SLUG,
        slug_length=20,
    )

    # Transfer ownership

    await conn.members.transfer_ownership(
        client=client,
        current_user_id=current_user_id,
        new_owner_user_id=invited_user_id,
        project_id=project_id,
    )

    # Remove the old owner
    
    await conn.members.delete(
        client=client,
        current_user_id=invited_user_id,
        invited_user_id=current_user_id,
        project_id=project_id
    )

    list_projects = await conn.projects.list_projects(client=client, current_user_id=current_user_id)
    assert len(list_projects) == 0

    # Delete the users
    
    await conn.users.delete(client=client, current_user_id=current_user_id)
    await conn.users.delete(client=client, current_user_id=invited_user_id)


    print(f'Test {test_id} ended successfully')

if __name__ == '__main__':
    asyncio.run(main())