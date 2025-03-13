from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from src.watsh.lib.exceptions import MemberNotFound, MemberAlreadyExist
from src.watsh.lib.models import Member
from .collections import DATABASE, MEMBERS_COLLECTION

async def create_member(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    user_id: ObjectId, 
    project_id: ObjectId
) -> ObjectId:
    """
    Create a new member association between a user and a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        user_id: ObjectId of the user.
        project_id: ObjectId of the project.
    Returns:
        ObjectId of the newly created member document.
    Raises:
        MemberAlreadyExist: Raised if the member already exists.
    """
    member = Member(user=user_id, project=project_id)
    try:
        result = await client[DATABASE][MEMBERS_COLLECTION].insert_one(
            member.model_dump(exclude_none=True, by_alias=True), session=session
        )
        return result.inserted_id
    except DuplicateKeyError:
        raise MemberAlreadyExist()

async def delete_member(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    user_id: ObjectId, 
    project_id: ObjectId
) -> None:
    """
    Delete a member association between a user and a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        user_id: ObjectId of the user.
        project_id: ObjectId of the project.
    """
    result = await client[DATABASE][MEMBERS_COLLECTION].delete_one(
        {'project': project_id, 'user': user_id}, session=session
    )

    if not result.deleted_count:
        raise MemberNotFound()

async def get_member(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    user_id: ObjectId
) -> Member:
    """
    Retrieve a member by project and user ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        user_id: ObjectId of the user.
    Returns:
        Member instance.
    Raises:
        MemberNotFound: Raised if the member is not found.
    """
    doc = await client[DATABASE][MEMBERS_COLLECTION].find_one(
        {'project': project_id, 'user': user_id}, session=session
    )
    if not doc:
        raise MemberNotFound()
    return Member(**doc)

async def list_memberships(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    filter_key: str, 
    filter_value: ObjectId
) -> list[Member]:
    """
    List memberships based on a filter key and value.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        filter_key: Field name to filter the memberships ('user' or 'project').
        filter_value: ObjectId value for the filter.
    Returns:
        List of Member instances.
    """
    cursor = client[DATABASE][MEMBERS_COLLECTION].find({filter_key: filter_value}, session=session)
    members = [Member(**doc) for doc in await cursor.to_list(None)]
    return members

async def list_user_memberships(client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId) -> list[Member]:
    """
    List all memberships of a user.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        user_id: ObjectId of the user.
    Returns:
        List of Member instances.
    """
    return await list_memberships(client, session, 'user', user_id)

async def list_project_members(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId) -> list[Member]:
    """
    List all members of a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
    Returns:
        List of Member instances.
    """
    return await list_memberships(client, session, 'project', project_id)


async def is_user_member_of_project(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    user_id: ObjectId
) -> bool:
    """
    Check if a user is a member of a specific project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to check.
        user_id: ObjectId of the user to check.
    Returns:
        bool: True if the user is a member of the project, False otherwise.
    """
    doc = await client[DATABASE][MEMBERS_COLLECTION].find_one(
        {'project': project_id, 'user': user_id}, session=session
    )
    return doc is not None