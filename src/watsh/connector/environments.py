from bson import ObjectId
from motor.core import AgnosticClient

from . import workflows, access_control, validation
from .crud import environments as crud_environments
from src.watsh.lib.models import Environment
from src.watsh.lib.exceptions import BadRequest

async def create(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    slug: str, 
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

            # Create the environment
            environment_id = await workflows.create_environment(
                client=client,
                session=session,
                project_id=project_id,
                slug=slug,
                default=False
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return environment_id

async def get(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    environment_id: ObjectId,
) -> Environment:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Get environment
            environment = await crud_environments.get_environment(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id
            )

            # Commit the transaction
            await session.commit_transaction()

    return environment


async def list_environments(
    client: AgnosticClient, current_user_id: ObjectId, project_id: ObjectId,
) -> list[Environment]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Get environments
            environments = await crud_environments.list_environments_per_project(
                client=client,
                session=session,
                project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()

    return environments


async def slug_update(
    client: AgnosticClient, 
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId, 
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

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Update the slug
            await crud_environments.update_slug(
                client=client, session=session, 
                project_id=project_id, environment_id=environment_id, slug=slug
            )

            # Commit the transaction
            await session.commit_transaction()



async def default_update(
    client: AgnosticClient, 
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId, 
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

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Get old default environment
            old_default_environement = await crud_environments.get_default_environment(
                client=client,
                session=session,
                project_id=project_id,
            )

            # Check if environent is not already default
            if old_default_environement.id == environment_id:
                raise BadRequest('This environment is already set as default.')

            # Update the environent
            await crud_environments.update_default(
                client=client, session=session, project_id=project_id,
                environment_id=old_default_environement.id, default=False
            )

            await crud_environments.update_default(
                client=client, session=session, project_id=project_id,
                environment_id=environment_id, default=True
            )

            # Commit the transaction
            await session.commit_transaction()



async def delete(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    environment_id: ObjectId,
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

            # Environment ID validation
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Delete environment
            await workflows.delete_environment(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id
            )

            # Commit the transaction
            await session.commit_transaction()


# async def archive_environment(
#     client: AgnosticClient, 
#     current_user_id: ObjectId, 
#     project_id: ObjectId, 
#     environment_id: ObjectId,
# ) -> ObjectId:
#     # Start a transaction to ensure that all the inserts are performed atomically.
#     async with await client.start_session() as session:
#         async with session.start_transaction():
            
#             # Access control
#             await access_control.user_authorization(
#                 client=client, session=session, project_id=project_id, user_id=current_user_id
#             )

#             # Verify project is not archived
#             validation.project_validation(
#                 client=client, session=session, project_id=project_id, check_is_not_archive=True
#             )

#             # Environment ID validation
#             validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id, check_is_not_archive=False
#             )

#             # Update the description on file
#             await crud_environments.archive_environment(
#                 client=client, session=session, 
#                 project_id=project_id, environment_id=environment_id,
#             )

#             # Commit the transaction
#             await session.commit_transaction()   


# async def unarchive_environment(
#     client: AgnosticClient, 
#     current_user_id: ObjectId, 
#     project_id: ObjectId, 
#     environment_id: ObjectId,
# ) -> ObjectId:
#     # Start a transaction to ensure that all the inserts are performed atomically.
#     async with await client.start_session() as session:
#         async with session.start_transaction():
            
#             # Access control
#             await access_control.user_authorization(
#                 client=client, session=session, project_id=project_id, user_id=current_user_id
#             )

#             # Verify project is not archived
#             validation.project_validation(
#                 client=client, session=session, project_id=project_id, check_is_not_archive=True
#             )

#             # Environment ID validation
#             validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id, check_is_not_archive=False
#             )

#             # Update the description on file
#             await crud_environments.unarchive_environment(
#                 client=client, session=session, 
#                 project_id=project_id, environment_id=environment_id,
#             )

#             # Commit the transaction
#             await session.commit_transaction()   
