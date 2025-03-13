import json
from typing import Annotated
from bson import ObjectId
from motor.core import AgnosticClient
from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, Query

from src.watsh.connector import access_control, validation, json_value as conn_json_value
from src.watsh.lib.models import User
from ..authentication import authenticate_user
from ..client import get_client


router = APIRouter(prefix="", tags=["ws"])


async def get_current_user_ws(
    token: Annotated[str, Query],
    client: AgnosticClient = Depends(get_client),
) -> User:
    """
    Retrieve the current user based on the provided HTTP authorization credentials.
    """
    return await authenticate_user(token, client)


async def common_dependency(
    project_id: str,
    environment_id: str,
    branch_id: str,
    current_user: User = Depends(get_current_user_ws),
    client: AgnosticClient = Depends(get_client),
) -> dict:
    return {
        "client": client,
        "current_user": current_user,
        "project_id": ObjectId(project_id),
        "environment_id": ObjectId(environment_id),
        "branch_id": ObjectId(branch_id),
    }

@router.websocket(path='/{project_id}/{environment_id}/{branch_id}')
async def websocket_endpoint(
    websocket: WebSocket, common_params: dict = Depends(common_dependency),
) -> None:
    await websocket.accept()
    try:
        await watsh(websocket=websocket, **common_params)
    except WebSocketDisconnect:
        pass


async def watsh(
    websocket: WebSocket, current_user: User, client: AgnosticClient, 
    project_id: ObjectId, environment_id: ObjectId, branch_id: ObjectId,
) -> None:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():

            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user.id
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
        
            # Commit the transaction
            await session.commit_transaction()

    # Pipeline
    resume_after = None
    pipeline = [{
        '$match': {
            'fullDocument.project': project_id,
            'fullDocument.environment': environment_id,
            'fullDocument.branch': branch_id,
        }
    }]

    async def send_snapshot() -> None:
        snapshot = await conn_json_value.get_json(
            client=client, current_user_id=current_user.id, 
            project_id=project_id, environment_id=environment_id, branch_id=branch_id,
        )
        await websocket.send_json(json.dumps(snapshot))
    
    async def start_stream(resume_after) -> None:
        # Connect to change stream
        async with client['watsh']['commits'].watch(
            full_document='updateLookup', 
            pipeline=pipeline, 
            resume_after=resume_after,
            max_await_time_ms=2000,
        ) as stream:
                
            if not resume_after:
                await send_snapshot()

            resume_after = stream.resume_token
            
            async for change in stream:
                operation = change['operationType']
                if operation == 'invalidate':
                    # An invalidate event occurs when an operation renders the change stream invalid
                    pass

                elif operation in ['insert', 'update', 'drop']:
                    await send_snapshot()

                else: 
                    raise Exception('Operation not implemented')

    await start_stream(resume_after)
        
    
