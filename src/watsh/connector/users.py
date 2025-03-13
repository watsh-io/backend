from bson import ObjectId
from motor.core import AgnosticClient

from . import workflows
from .crud import (
    environments as crud_environments, projects as crud_projects, members as crud_members,
    branches as crud_branches, users as crud_users
)
from src.watsh.lib.models import User, UserSnapshot, ProjectSnapshot, EnvironmentSnapshot


async def create(client: AgnosticClient, email: str, create_sample_project: bool = True) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():

            # Create user
            user_id = await workflows.create_user(client, session, email, create_sample_project)

            # Commit the transaction
            await session.commit_transaction()
    
    return user_id


async def get(client: AgnosticClient, current_user_id: ObjectId) -> User:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Get user
            user = await crud_users.get_user(client=client, session=session, user_id=current_user_id)

            # Commit the transaction
            await session.commit_transaction()

    return user


async def get_by_email(client: AgnosticClient, email: str) -> User:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Get user
            user = await crud_users.get_user_by_email(client=client, session=session, email=email)

            # Commit the transaction
            await session.commit_transaction()

    return user


async def is_email_registered(client: AgnosticClient, email: str) -> bool:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Get user
            result = await crud_users.check_user_exists_by_email(client, session, email)

            await session.commit_transaction()

    return result


async def email_update(client: AgnosticClient, current_user_id: ObjectId, email: str) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Update email
            await crud_users.update_user_email(client, session, current_user_id, email)

            # Commit the transaction
            await session.commit_transaction()


async def delete(client: AgnosticClient, current_user_id: ObjectId) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Delete user
            await workflows.delete_user(client, session, current_user_id)

            # Commit the transaction
            await session.commit_transaction()



async def get_user_snapshot(
    client: AgnosticClient, current_user: User
) -> UserSnapshot:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            list_project_memberships = await crud_members.list_user_memberships(
                client=client, session=session, user_id=current_user.id
            )

            list_project_snapshots: list[ProjectSnapshot] = []
            for membership in list_project_memberships:
                
                project = await crud_projects.find_project(
                    client=client, session=session, project_id=membership.project
                )

                list_project_members = await crud_members.list_project_members(
                    client=client, session=session, project_id=membership.project
                )

                list_snapshot_environments: list[EnvironmentSnapshot] = []
                list_project_environments = await crud_environments.list_environments_per_project(
                    client=client, session=session, project_id=membership.project
                )
                for project_environment in list_project_environments:
                    list_branches = await crud_branches.list_branches_per_environment(
                        client=client, session=session, project_id=membership.project, environment_id=project_environment.id
                    )

                    snapshot_environment = EnvironmentSnapshot(
                        environment=project_environment,
                        branches=list_branches
                    )

                    list_snapshot_environments.append(snapshot_environment)

                project_snapshot = ProjectSnapshot(
                    project=project,
                    members=list_project_members,
                    environments=list_snapshot_environments,
                )
                
                list_project_snapshots.append(project_snapshot)

            # Commit the transaction
            await session.commit_transaction()


    user_snapshot = UserSnapshot(
        user=current_user,
        projects=list_project_snapshots
    )
     
    return user_snapshot