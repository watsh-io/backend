from bson import ObjectId
from motor.core import AgnosticClient

from . import workflows, access_control, validation
from .crud import members as crud_members, projects as crud_projects
from src.watsh.lib.models import Project
from src.watsh.lib.exceptions import UnauthorizedException



async def create(
    client: AgnosticClient,
    current_user_id: ObjectId,
    slug: str, 
    description: str,
    create_sample_environments: bool = True,
) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():

            # Create the project
            project_id = await workflows.create_project(
                client=client,
                session=session,
                slug=slug,
                description=description,
                owner=current_user_id,
                create_sample_environments=create_sample_environments
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return project_id

    
async def get(
    client: AgnosticClient, current_user_id: ObjectId, project_id: ObjectId
) -> Project:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():

            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Fetch the project
            project = await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=False
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return project


async def list_projects(
    client: AgnosticClient, current_user_id: ObjectId
) -> list[Project]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Get memberships
            list_memberships = await crud_members.list_user_memberships(
                client=client,
                session=session,
                user_id=current_user_id
            )

            results = []

            for membership in list_memberships:
                project = await crud_projects.find_project(
                    client=client, session=session, project_id=membership.project
                )
                results.append(project)

    return results


async def slug_update(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    slug: str,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Update the slug
            await crud_projects.update_slug(
                client=client, session=session, project_id=project_id, slug=slug
            )

            # Commit the transaction
            await session.commit_transaction()


async def description_update(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    description: str,
) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )

            # Update the slug
            await crud_projects.update_description(
                client=client, session=session, project_id=project_id, description=description
            )

            # Commit the transaction
            await session.commit_transaction()   


async def archive_project(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            if not await crud_projects.is_user_owner(
                client=client, session=session, project_id=project_id, user_id=current_user_id,
            ):
                raise UnauthorizedException("Only the project owner can perform this action.")

            # Archive
            await crud_projects.archive_project(
                client=client, session=session, project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()   


async def unarchive_project(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            if not await crud_projects.is_user_owner(
                client=client, session=session, project_id=project_id, user_id=current_user_id,
            ):
                raise UnauthorizedException("Only the project owner can perform this action.")

            # Unarchive
            await crud_projects.unarchive_project(
                client=client, session=session, project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()   


async def delete(
    client: AgnosticClient, current_user_id: ObjectId, project_id: ObjectId
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            if not await crud_projects.is_user_owner(
                client=client, session=session, project_id=project_id, user_id=current_user_id,
            ):
                raise UnauthorizedException("Only the project owner can perform this action.")

            # Delete the project
            await workflows.delete_project(
                client=client,
                session=session,
                project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()


async def is_user_owner(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
) -> bool:    
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Validate the request
            result = await crud_projects.is_user_owner(
                client=client, session=session, project_id=project_id, user_id=current_user_id,
            )

            # Commit the transaction
            await session.commit_transaction()

    return result