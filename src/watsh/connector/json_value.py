from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession

from . import access_control, validation
from .items import verify_secret
from .crud import items as crud_items, commits as crud_commits
from src.watsh.lib.models import ItemType
from src.watsh.lib.pyobjectid import NULL_OBJECTID
from src.watsh.lib.crypto import decrypt


async def _get_nested_json(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    aes_password: str,
) -> dict:
    
    items = await crud_items.list_items_per_parent(
        client=client, session=session, project_id=project_id, environment_id=environment_id,
        branch_id=branch_id, parent_id=parent_id,
    )

    result = {}

    for item in items:
        if item.type == ItemType.OBJECT.value:
            result[item.slug] = await _get_nested_json(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=item.item,
                aes_password=aes_password
            )
        
        # elif item.type == ItemType.ARRAY.value:

        else:
            if item.secret_active:
                decrypted_secret = decrypt(aes_password, item.secret_value)
                casted_secret = verify_secret(item.type, decrypted_secret)
                result[item.slug] = casted_secret

    return result


async def get_json(
    client: AgnosticClient,
    current_user_id: ObjectId,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    aes_password: str,
) -> dict:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Values
            values = await _get_nested_json(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=NULL_OBJECTID,
                aes_password=aes_password,
            )

            # Commit the transaction
            await session.commit_transaction()

    return values




async def _get_nested_json_per_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    commit_timestamp: int,
    aes_password: str,
) -> dict:
    
    items = await crud_items.list_items_per_commit_per_parent(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
        parent_id=parent_id,
        commit_timestamp=commit_timestamp
    )

    result = {}

    for item in items:
        if item.type == ItemType.OBJECT.value:
            result[item.slug] = await _get_nested_json_per_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=item.item,
                commit_timestamp=commit_timestamp,
                aes_password=aes_password
            )
        
        # elif item.type == ItemType.ARRAY.value:
        # ...

        else:
            if item.secret_active:
                decrypted_secret = decrypt(aes_password, item.secret_value)
                casted_secret = verify_secret(item.type, decrypted_secret)
                result[item.slug] = casted_secret

    return result


async def get_json_per_commit(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_id: ObjectId,
    aes_password: str,
) -> dict:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get commit
            commit = await crud_commits.get_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                commit_id=commit_id,
            )


            # Values
            values = await _get_nested_json_per_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=NULL_OBJECTID,
                commit_timestamp=commit.timestamp,
                aes_password=aes_password,
            )

            # Commit the transaction
            await session.commit_transaction()

    return values
