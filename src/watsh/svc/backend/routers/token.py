from datetime import datetime, timezone, timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status

from src.watsh.lib.exceptions import TokenHandlingError
from src.watsh.lib.models import Token, User
from src.watsh.lib.token import create_token, decode_token
from ..authentication import get_current_user
from ..config import JWT_SECRET, JWT_ALGORITHM

router = APIRouter(prefix="/token", tags=["token"])

# Constants for time durations and timestamp length
ONE_YEAR = timedelta(days=365)
FIFTEEN_MINUTES = timedelta(minutes=15)
TIMESTAMP_LENGTH_SECONDS = 10


def validate_and_convert_expiration(expiration: int) -> datetime:
    """
    Validate the expiration timestamp and convert it to a datetime object.
    Raises ValueError if the expiration is not within the allowed range.
    """
    current_time = datetime.now(timezone.utc)
    if len(str(expiration)) > TIMESTAMP_LENGTH_SECONDS:
        expiration /= 1000  # Convert milliseconds to seconds
    expiration_time = datetime.fromtimestamp(expiration, timezone.utc)
    if expiration_time > current_time + ONE_YEAR:
        raise ValueError('Expiration must be less than 1 year from today.')
    if expiration_time < current_time + FIFTEEN_MINUTES:
        raise ValueError('Expiration must be at least 15 minutes from now.')
    return expiration_time

@router.post('', response_model=Token)
async def post_token(
    expiration: int,
    current_user: Annotated[User, Depends(get_current_user)]
) -> Token:
    """
    Create a new token with a custom expiration time.
    """
    try:
        expiration_time = validate_and_convert_expiration(expiration)
    except ValueError as exc:
        print(exc)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(exc))

    payload = {'user_id': str(current_user.id), 'exp': expiration_time}
    access_token = create_token(payload, JWT_SECRET, JWT_ALGORITHM)
    return Token(access_token=access_token, token_type='bearer')

@router.get('', response_model=Token)
async def get_token(login_token: str) -> Token:
    """
    Generate a new access token using a login token.
    """
    try:
        payload = decode_token(login_token, JWT_SECRET, JWT_ALGORITHM)
    except TokenHandlingError:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid or expired login token.")

    new_payload = {'user_id': payload['user_id'], 'exp': datetime.utcnow() + timedelta(hours=24)}
    access_token = create_token(new_payload, JWT_SECRET, JWT_ALGORITHM)
    return Token(access_token=access_token, token_type='bearer')
