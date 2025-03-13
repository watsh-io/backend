import datetime
from bson import ObjectId
from typing import Annotated
from pydantic import EmailStr
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Response, Query, HTTPException
from fastapi.responses import RedirectResponse

from src.watsh.connector import members as conn_members, projects as conn_projects
from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.models import User
from src.watsh.lib.token import decode_token, create_token
from src.watsh.lib.exceptions import TokenHandlingError
from ..mailing.invite_user import send_invite_user_message
from ..authentication import get_current_user
from ..client import get_client
from ..smtp import get_smtp_client
from ..config import JWT_SECRET, JWT_ALGORITHM, WATSH_APP, DOMAIN

router = APIRouter(prefix="/member", tags=["member"])



@router.get('/{project_id}', status_code=status.HTTP_200_OK)
async def get_members(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> list[User]:
    return await conn_members.list_users(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
    )

@router.delete('/{project_id}/{user_id}', status_code=status.HTTP_200_OK)
async def delete_member(
    project_id: str, user_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    if current_user.id == user_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'You cannot remove yourself. Please either delete this project or transfer the ownership before removing yourself from the project.')
    
    await conn_members.delete(
        client=client, 
        current_user_id=current_user.id, 
        invited_user_id=ObjectId(user_id),
        project_id=ObjectId(project_id),
    )    
    return Response(status_code=status.HTTP_200_OK)


@router.post('/{project_id}/invite', status_code=status.HTTP_201_CREATED)
async def send_invite(
    project_id: str, 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
    smtp_client: SMTPClientManager = Depends(get_smtp_client),
    email: Annotated[list[EmailStr], Query(description="List of emails")] = [], 
    emails: Annotated[str, Query(description="Comma seperated list of emails")] = '',
) -> None:
    list_emails = email + emails.split(',')
    
    if not list_emails:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'You must provide at least one email.')
    
    # Get the project information (and access control)
    project = await conn_projects.get(
        client=client, current_user_id=current_user.id, project_id=ObjectId(project_id)
    )

    # Get current list of users
    users = await conn_members.list_users(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
    )
    project_email_addresses = [user.email for user in users]

    # For each email address
    for email_address in list_emails:
        # Check input
        if current_user.email == email_address:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'You cannot invite yourself.')
        
        # Verify the user is not already in the project
        if email_address in project_email_addresses:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f'{email_address} is already on the project.')
    
    # Send the emails
    for email_address in list_emails:
        await send_invite_user_message(
            smtp_client=smtp_client, project=project, recipient_email_address=email_address,
            sender_email_address=current_user.email
        )

    return Response(status_code=status.HTTP_201_CREATED)


@router.get('/{project_id}/invite/accept')
async def send_invite(
    project_id: str,
    invite_token: str, 
    client: AgnosticClient = Depends(get_client),
) -> None:
    # Decode the payload
    try:
        payload = decode_token(invite_token, JWT_SECRET, JWT_ALGORITHM)
    except TokenHandlingError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

    # Accept invitation
    user_id = await conn_members.accept_invitation(
        client=client,
        project_id=ObjectId(payload['project_id']),
        email=payload['email']
    )

    # TODO: Redirect user to dashboard with access_token
    # Redirect to dashboard with a token
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(hours=24)
    payload = {'user_id': str(user_id), 'exp': expiration_time}
    access_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)
    redirect_url = f"{WATSH_APP}?access_token={access_token}&host={DOMAIN}"
    return RedirectResponse(url=redirect_url)


