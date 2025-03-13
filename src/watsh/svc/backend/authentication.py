from bson import ObjectId
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from motor.core import AgnosticClient

from src.watsh.connector import users as conn_users
from src.watsh.lib.models import User
from src.watsh.lib.token import decode_token
from src.watsh.lib.exceptions import TokenHandlingError, UserNotFound

from .client import get_client
from .config import JWT_ALGORITHM, JWT_SECRET

# Define HTTP Bearer Scheme
scheme = HTTPBearer()

async def get_current_user(
    authorization: HTTPAuthorizationCredentials = Depends(scheme),
    client: AgnosticClient = Depends(get_client),
) -> User:
    """
    Retrieve the current user based on the provided HTTP authorization credentials.
    """
    token = authorization.credentials
    return await authenticate_user(token, client)

async def authenticate_user(token: str, client: AgnosticClient) -> User:
    """
    Authenticate the user based on the provided token and return the user details.
    """
    user_id = decode_token_or_raise(token)
    return await get_user_or_raise(user_id, client)

def decode_token_or_raise(token: str) -> str:
    """
    Decode the JWT token or raise HTTPForbidden on failure.
    """
    try:
        payload = decode_token(token, JWT_SECRET, JWT_ALGORITHM)
        return payload['user_id']
    except TokenHandlingError as err:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=(str(err)))

async def get_user_or_raise(user_id: str, client: AgnosticClient) -> User:
    """
    Retrieve a user by ID from the database or raise HTTPForbidden if not found.
    """
    try:
        return await conn_users.get(
            client=client, current_user_id=ObjectId(user_id)
        )
    except UserNotFound:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail='Your account has been deleted.')
