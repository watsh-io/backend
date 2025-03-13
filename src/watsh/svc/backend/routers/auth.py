import datetime
from motor.core import AgnosticClient
from fastapi import APIRouter, Depends, HTTPException, status, Response
from fastapi.responses import RedirectResponse
from pydantic import EmailStr

from src.watsh.connector import users as conn_users
from src.watsh.lib.smtp_client import SMTPClientManager
from src.watsh.lib.token import decode_token, create_token
from src.watsh.lib.exceptions import UserNotFound, TokenHandlingError
from ..mailing.validate_email_address import send_validate_address_email
from ..mailing.login_token import send_login_email
from ..client import get_client
from ..smtp import get_smtp_client
from ..config import WATSH_LANDING_URL, JWT_SECRET, JWT_ALGORITHM, WATSH_APP, DOMAIN

router = APIRouter(prefix="", tags=["authentication"])



@router.get("/signup")
async def signup(
    email: EmailStr,
    client: AgnosticClient = Depends(get_client),
    smtp_client: SMTPClientManager = Depends(get_smtp_client),
) -> None:
    if await conn_users.is_email_registered(client, email):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail='Email address already registered.')
    await send_validate_address_email(email_address=email, smtp_client=smtp_client)
    return Response(status_code=status.HTTP_200_OK)


@router.get("/register")
async def register(
    registration_token: str,
    client: AgnosticClient = Depends(get_client),
) -> None:
    # Decode registration token
    try:
        payload = decode_token(registration_token, JWT_SECRET, JWT_ALGORITHM)
    except TokenHandlingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid token.")

    # Create user on the backend database
    email_address = payload['email']
    if not await conn_users.is_email_registered(client, email_address):    
        user_id = await conn_users.create(client=client, email=email_address, create_sample_project=False)
    else:
        user = await conn_users.get_by_email(client=client, email=email_address)
        user_id = user.id
        
    expiration_time = datetime.datetime.utcnow() + datetime.timedelta(minutes=15)
    payload = {'user_id': str(user_id), 'exp': expiration_time}
    access_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)
    
    # Redirect to dashboard with a token
    redirect_url = f"{WATSH_APP}?access_token={access_token}" + ("" if DOMAIN == "https://api.watsh.io" else f"&host={DOMAIN}")
    return RedirectResponse(url=redirect_url)

@router.get("/logout", status_code=status.HTTP_302_FOUND)
async def logout() -> RedirectResponse:
    return RedirectResponse(url=WATSH_LANDING_URL)


@router.get("/login")
async def login(
    email: EmailStr,
    client: AgnosticClient = Depends(get_client),
    smtp_client: SMTPClientManager = Depends(get_smtp_client),
) -> None:
    try:
        user = await conn_users.get_by_email(client, email)
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email not registered.")
    
    await send_login_email(user, smtp_client)
    return Response(status_code=status.HTTP_200_OK)
