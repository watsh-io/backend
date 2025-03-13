from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from src.watsh.lib.models import User
from src.watsh.lib.exceptions import UserNotFound, EmailAlreadyTaken
from .collections import DATABASE, USERS_COLLECTION

async def _find_user_document(client: AgnosticClient, session: AgnosticClientSession, query: dict) -> dict:
    """
    Private helper to find a single user document in the database.
    Args:
        client: The database client.
        session: The current client session for transactional support.
        query: The query dictionary to find the user.
    Returns:
        The found user document as a dictionary.
    Raises:
        UserNotFound: If no user matches the query.
    """
    doc = await client[DATABASE][USERS_COLLECTION].find_one(query, session=session)
    if not doc:
        raise UserNotFound()
    return doc

async def get_user(client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId) -> User:
    """
    Retrieve a user by their unique ObjectId.
    Args:
        client: The database client.
        session: The current client session.
        user_id: The ObjectId of the user to retrieve.
    Returns:
        A User model instance of the found user.
    """
    doc = await _find_user_document(client, session, {'_id': user_id})
    return User(**doc)

async def get_user_by_email(client: AgnosticClient, session: AgnosticClientSession, email: str) -> User:
    """
    Retrieve a user by their email address.
    Args:
        client: The database client.
        session: The current client session.
        email: The email address of the user.
    Returns:
        A User model instance of the found user.
    """
    doc = await _find_user_document(client, session, {'email': email})
    return User(**doc)

async def create_user(client: AgnosticClient, session: AgnosticClientSession, email: str) -> ObjectId:
    """
    Create a new user in the database.
    Args:
        client: The database client.
        session: The current client session.
        email: The email address of the new user.
    Returns:
        The ObjectId of the newly created user.
    Raises:
        EmailAlreadyTaken: If the email is already in use.
    """
    user = User(email=email)
    try:
        result = await client[DATABASE][USERS_COLLECTION].insert_one(
            user.model_dump(exclude_none=True, by_alias=True),
            session=session
        )
        return result.inserted_id
    except DuplicateKeyError:
        raise EmailAlreadyTaken()

async def check_user_exists_by_email(client: AgnosticClient, session: AgnosticClientSession, email: str) -> bool:
    """
    Check if a user exists by their email address.
    Args:
        client: The database client.
        session: The current client session.
        email: The email address to check.
    Returns:
        True if the user exists, False otherwise.
    """
    doc = await client[DATABASE][USERS_COLLECTION].find_one({'email': email}, session=session)
    return doc is not None

async def update_user_email(client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId, email: str) -> None:
    """
    Update the email address of a user.
    Args:
        client: The database client.
        session: The current client session.
        user_id: The ObjectId of the user to update.
        email: The new email address.
    Raises:
        EmailAlreadyTaken: If the email is already in use.
    """
    try:
        await client[DATABASE][USERS_COLLECTION].update_one(
            {'_id': user_id}, {'$set': {'email': email}}, session=session
        )
    except DuplicateKeyError:
        raise EmailAlreadyTaken()

async def delete_user(client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId) -> None:
    """
    Delete a user from the database.
    Args:
        client: The database client.
        session: The current client session.
        user_id: The ObjectId of the user to delete.
    """
    result = await client[DATABASE][USERS_COLLECTION].delete_one({'_id': user_id}, session=session)
    if not result.deleted_count:
        raise UserNotFound()