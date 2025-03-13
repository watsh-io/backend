from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Response, HTTPException

from src.watsh.connector import members as conn_members, projects as conn_projects
from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.models import User
from src.watsh.lib.token import decode_token
from ..authentication import get_current_user
from ..client import get_client
from ..smtp import get_smtp_client
from ..config import JWT_SECRET, JWT_ALGORITHM
from ..mailing.ownership_transfer import send_ownership_transfer

router = APIRouter(prefix="/ownership", tags=["ownership"])


@router.patch('/{project_id}')
async def transfer_ownership(
    project_id: str, 
    email: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
    smtp_client: SMTPClientManager = Depends(get_smtp_client),
) -> None:
    # Verify user is current owner (access control)
    if not await conn_projects.is_user_owner(
        client=client, current_user_id=current_user.id, project_id=ObjectId(project_id)
    ):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Only the project owner can transfer the ownership.')
    
    # Verify not self invitation
    if current_user.email == email:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'You cannot transfer ownership to yourself.')
    
    # Get project
    project = await conn_projects.get(
        client=client, current_user_id=current_user.id, project_id=ObjectId(project_id)
    )

    # Send email
    await send_ownership_transfer(smtp_client=smtp_client, project=project, recipient_email_address=email, sender_email_address=current_user.email)
    return Response(status_code=status.HTTP_200_OK)

@router.get('/{project_id}/accept', status_code=status.HTTP_201_CREATED)
async def accept_ownership(
    project_id: str,
    transfer_ownership_token: str, 
    client: AgnosticClient = Depends(get_client),
) -> None:
    # Decode the payload
    payload = decode_token(transfer_ownership_token, JWT_SECRET, JWT_ALGORITHM)

    # Accept ownserhip
    await conn_members.transfer_ownership(
        client=client,
        new_owner_email=payload['email'],
        project_id=ObjectId(payload['project_id']),
    )

    return Response(status_code=status.HTTP_201_CREATED)