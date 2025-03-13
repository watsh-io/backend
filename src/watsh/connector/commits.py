from bson import ObjectId
from motor.core import AgnosticClient

from . import access_control, validation
from .crud import commits as crud_commits
from src.watsh.lib.models import Commit



async def list_commits(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> list[Commit]:
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

            # Branch id validation
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get commits
            results = await crud_commits.list_commits(
                client=client, session=session, project_id=project_id, 
                environment_id=environment_id, branch_id=branch_id
            )

            # Commit the transaction
            await session.commit_transaction()
    
    return results



# TODO: rollback