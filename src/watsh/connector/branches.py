from bson import ObjectId
from motor.core import AgnosticClient

from . import workflows, access_control, validation
from .crud import branches as crud_branches
from src.watsh.lib.models import Branch
from src.watsh.lib.exceptions import BadRequest

async def create(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
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

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Create the branch
            branch_id = await crud_branches.create_branch(
                client=client, session=session, project_id=project_id, 
                environment_id=environment_id, slug=slug, default=False,
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return branch_id



async def get(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> Branch:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Get branch
            branch = await crud_branches.get_branch(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
            )

            # Commit the transaction
            await session.commit_transaction()

    return branch


async def list_branches(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
) -> list[Branch]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Environment id validation
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Get branches
            branches = await crud_branches.list_branches_per_environment(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
            )

            # Commit the transaction
            await session.commit_transaction()

    return branches


async def slug_update(
    client: AgnosticClient, 
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId, 
    branch_id: ObjectId,
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

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Update the slug
            await crud_branches.update_slug(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
                branch_id=branch_id, slug=slug
            )

            # Commit the transaction
            await session.commit_transaction()


async def delete(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
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

            # Verify branch ID
            branch = await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            if branch.default:
                raise BadRequest('Default branch cannot be deleted.')

            # Delete branch
            await workflows.delete_branch(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
            )

            # Commit the transaction
            await session.commit_transaction()


# async def archive_update(
#     client: AgnosticClient, 
#     current_user_id: ObjectId,
#     project_id: ObjectId,
#     environment_id: ObjectId, 
#     branch_id: ObjectId,
# ) -> None:
#     # Start a transaction to ensure that all the inserts are performed atomically.
#     async with await client.start_session() as session:
#         async with session.start_transaction():
            
#             # Access control
#             await access_control.user_authorization(
#                 client=client, session=session, project_id=project_id, user_id=current_user_id
#             )

#             # Verify project is not archived
#             await validation.project_validation(
#                 client=client, session=session, project_id=project_id, check_is_not_archive=True
#             )

#             # Verify environment ID
#             await validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id,
#             )

#             # Branch id validation
#             await validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id,
#                 branch_id=branch_id, check_is_not_archive=False
#             )

#             # Archve the branch
#             await crud_branches.archive_branch(
#                 client=client, session=session, project_id=project_id,
#                 environment_id=environment_id, branch_id=branch_id
#             )

#             # Commit the transaction
#             await session.commit_transaction()


# async def unarchive_update(
#     client: AgnosticClient, 
#     current_user_id: ObjectId,
#     project_id: ObjectId,
#     environment_id: ObjectId, 
#     branch_id: ObjectId,
# ) -> None:
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

#             # Verify environment ID and environement is not archived.
#             validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id, check_is_not_archive=True
#             )

#             # Branch id validation
#             validation.environment_validation(
#                 client=client, session=session, project_id=project_id, environment_id=environment_id,
#                 branch_id=branch_id, check_is_not_archive=False
#             )

#             # Archve the branch
#             await crud_branches.unarchive_branch(
#                 client=client, session=session, project_id=project_id,
#                 environment_id=environment_id, branch_id=branch_id
#             )

#             # Commit the transaction
#             await session.commit_transaction()


async def default_update(
    client: AgnosticClient, 
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId, 
    branch_id: ObjectId,
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

            # Verify branch ID 
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id,
            )

            # Get old default branch
            old_default_branch = await crud_branches.get_default_branch(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
            )

            # Check if branch is not already default
            if old_default_branch.id == branch_id:
                raise BadRequest('This branch is already set as default.')

            # Update the branch
            await crud_branches.update_default(
                client=client, session=session, project_id=project_id,
                environment_id=environment_id, branch_id=old_default_branch.id, default=False
            )

            await crud_branches.update_default(
                client=client, session=session, project_id=project_id,
                environment_id=environment_id, branch_id=branch_id, default=True
            )
        
            # Commit the transaction
            await session.commit_transaction()