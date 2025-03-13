import uuid
import asyncio
from pymongo.server_api import ServerApi
from motor.motor_asyncio import AsyncIOMotorClient

import src.watsh.connector as conn
import watsh.lib.exceptions as exceptions
from src.watsh.lib.models import ItemType
from watsh.lib.pyobjectid import SET_SLUG, NULL_OBJECTID

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

    # Get first user project

    list_projects = await conn.projects.list_projects(client=client, current_user_id=current_user_id)
    project_id = list_projects[0].id

    list_environments = await conn.environments.list_environments(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id
    )
    environment_id = list_environments[0].id
    
    list_branches = await conn.branches.list_branches(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        environment_id=environment_id
    )
    branch_id = list_branches[0].id

    # Create item

    item_id = await conn.items.create(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
        parent_id=NULL_OBJECTID,
        item_type=ItemType.STRING,
        slug='key-1',
        slug_set=SET_SLUG,
        slug_length=20,
        commit_message='First item',
    )

    # Get list of items

    list_branch_items = await conn.items.list_branch_items(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id
    )

    assert len(list_branch_items) == 1

    # Update item
    new_slug = 'new-key-1'

    await conn.items.slug_update(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
        item_id=item_id,
        slug=new_slug,
        slug_set=SET_SLUG,
        slug_length=20,
        commit_message='New slug',
    )

    # Get item

    item = await conn.items.get(
       client=client,
       current_user_id=current_user_id,
       project_id=project_id,
       environment_id=environment_id,
       branch_id=branch_id,
       item_id=item_id
    )

    assert item.item == item_id
    assert item.slug == new_slug

    # Get commits
    list_commits = await conn.commits.list_commits(
        client=client,
        current_user_id=current_user_id,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
    )

    assert len(list_commits) == 2

    # Delete the users
    
    await conn.users.delete(client=client, current_user_id=current_user_id)

    print(f'Test {test_id} ended successfully')

if __name__ == '__main__':
    asyncio.run(main())