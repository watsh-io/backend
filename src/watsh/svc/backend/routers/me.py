from bson import ObjectId
from typing import Annotated
from pydantic import EmailStr
from fastapi import APIRouter, status, Depends, HTTPException
from motor.core import AgnosticClient

from src.watsh.connector import users as conn_users
from src.watsh.lib.models import User, UserSnapshot
from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.exceptions import TokenHandlingError
from src.watsh.lib.token import decode_token

from ..mailing.update_email_address import send_update_address_email
from ..authentication import get_current_user
from ..client import get_client
from ..smtp import get_smtp_client
from ..config import JWT_SECRET, JWT_ALGORITHM


router = APIRouter(prefix="/me", tags=["me"])


@router.get(path='', response_model=User)
async def get_me(current_user: Annotated[User, Depends(get_current_user)]) -> User:
    """
    Retrieve the current user's information.
    """
    return current_user

@router.delete(path='', status_code=status.HTTP_204_NO_CONTENT)
async def delete_me(
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client)
) -> None:
    """
    Delete the current user's account.
    """
    await conn_users.delete(client=client, current_user_id=current_user.id)
    

@router.patch("/email", status_code=status.HTTP_204_NO_CONTENT)
async def request_email_update(
    email: EmailStr,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
    smtp_client: SMTPClientManager = Depends(get_smtp_client),
) -> None:
    if await conn_users.is_email_registered(client, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='This email is already registered.')

    await send_update_address_email(current_user, email, smtp_client)


@router.get("/email/accept", status_code=status.HTTP_200_OK)
async def patch_email_accept(
    verification_token: str,
    client: AgnosticClient = Depends(get_client),
) -> None:
    try:
        payload = decode_token(verification_token, JWT_SECRET, JWT_ALGORITHM)
    except TokenHandlingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired verification token.")
    
    await conn_users.email_update(client, ObjectId(payload['user_id']), payload['email'])
    # Redirect user to dashboard with a token (implementation depends on the frontend)
    # return RedirectResponse(url=f"{DASHBOARD_URL}?token={new_token}")


@router.get('/snapshot', status_code=status.HTTP_200_OK)
async def get_me_snapshot(
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> UserSnapshot:
    return await conn_users.get_user_snapshot(
        client=client, current_user=current_user
    )