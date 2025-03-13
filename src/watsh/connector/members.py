from bson import ObjectId
from motor.core import AgnosticClient

from . import access_control, validation
from .crud import users as crud_users, members as crud_members, projects as crud_projects
from src.watsh.lib.models import User
from src.watsh.lib.exceptions import BadRequest, UnauthorizedException



async def list_users(
    client: AgnosticClient, current_user_id: ObjectId, project_id: ObjectId
) -> list[User]:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Fetch members of project
            list_members = await crud_members.list_project_members(
                client=client,
                session=session,
                project_id=project_id
            )

            results = []

            for member in list_members:
                user = await crud_users.get_user(client=client, session=session, user_id=member.user) 
                results.append(user)

            # Commit the transaction
            await session.commit_transaction()

    return results


async def transfer_ownership(
    client: AgnosticClient, 
    new_owner_email: str, 
    project_id: ObjectId,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # If user already has an account
            if await crud_users.check_user_exists_by_email(
                client=client,
                session=session,
                email=new_owner_email,
            ):
                # Get user information
                user = await crud_users.get_user_by_email(
                    client=client,
                    session=session,
                    email=new_owner_email,
                )
                user_id = user.id

                # Check transfer is not already done
                if await crud_projects.is_user_owner(
                    client=client, session=session, project_id=project_id, user_id=user_id
                ):
                    raise BadRequest('You are already the owner of this project.')

            else:
                # Create user
                user_id = await crud_users.create_user(client, session, new_owner_email)

            # Create membership if it does not exist
            if not crud_members.is_user_member_of_project(
                client=client, session=session, project_id=project_id, user_id=user_id
            ):
                await crud_members.create_member(
                    client=client, 
                    session=session, 
                    user_id=user_id, 
                    project_id=project_id
                )

            # Transfer ownership
            await crud_projects.update_owner(
                client=client, session=session, project_id=project_id, owner_id=user_id
            )
                
            # Commit the transaction
            await session.commit_transaction()



async def delete(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    invited_user_id: ObjectId, 
    project_id: ObjectId,
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

            # Validate the request
            if await crud_projects.is_user_owner(
                client=client, session=session, project_id=project_id, user_id=invited_user_id
            ):
                raise UnauthorizedException('Project owner cannot be removed.')


            # Delete member
            await crud_members.delete_member(
                client=client,
                session=session,
                user_id=invited_user_id,
                project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()



async def accept_invitation(
    client: AgnosticClient,
    project_id: ObjectId,
    email: str,
) -> ObjectId:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Verify project is not archived
            await validation.project_validation(
                client=client, session=session, project_id=project_id, check_is_not_archive=True
            )
            
            # If user already exist
            if await crud_users.check_user_exists_by_email(
                client=client, session=session, email=email,
            ):
                user = await crud_users.get_user_by_email(
                    client=client, session=session, email=email
                )
                user_id = user.id

                if not await crud_members.is_user_member_of_project(
                    client=client, session=session, project_id=project_id, user_id=user.id
                ):
                    await crud_members.create_member(
                        client=client, 
                        session=session, 
                        project_id=project_id, 
                        user_id=user_id
                    )

            # If user does not exist
            else:
                user_id = await crud_users.create_user(client, session, email)
                await crud_members.create_member(
                    client=client, 
                    session=session, 
                    project_id=project_id, 
                    user_id=user_id
                )
            
            # Commit the transaction
            await session.commit_transaction()
    
    return user_id