from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from src.watsh.lib.exceptions import ProjectSlugTaken, ProjetNotFound
from src.watsh.lib.models import Project
from .collections import DATABASE, PROJECTS_COLLECTION

async def create_project(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    slug: str,
    description: str,
    owner: ObjectId
) -> ObjectId:
    """
    Create a new project in the database.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        slug: Unique identifier for the project.
        description: Description of the project.
        owner: ObjectId of the project owner.
    Returns:
        ObjectId of the newly created project.
    Raises:
        ProjectSlugTaken: Raised if the slug is already in use.
    """
    project = Project(slug=slug, description=description, owner=owner, archived=False)
    try:
        result = await client[DATABASE][PROJECTS_COLLECTION].insert_one(
            project.model_dump(exclude_none=True, by_alias=True), session=session
        )
        return result.inserted_id
    except DuplicateKeyError:
        raise ProjectSlugTaken()

async def find_project(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId) -> Project:
    """
    Find a project by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to find.
    Returns:
        Project instance.
    Raises:
        ProjetNotFound: Raised if the project is not found.
    """
    project_doc = await client[DATABASE][PROJECTS_COLLECTION].find_one({'_id': project_id}, session=session)
    if not project_doc:
        raise ProjetNotFound()
    return Project(**project_doc)

async def update_project(
    client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, update_data: dict
) -> None:
    """
    Update a project with the given update data.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to update.
        update_data: Dictionary containing update fields and values.
    Raises:
        ProjectSlugTaken: Raised if an update violates unique constraints.
    """
    try:
        await client[DATABASE][PROJECTS_COLLECTION].update_one(
            {'_id': project_id}, {'$set': update_data}, session=session
        )
    except DuplicateKeyError:
        raise ProjectSlugTaken()

async def delete_project(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId) -> None:
    """
    Delete a project by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to delete.
    """
    result = await client[DATABASE][PROJECTS_COLLECTION].delete_one({'_id': project_id}, session=session)
    if not result.deleted_count:
        raise ProjetNotFound()
    
async def archive_project(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId) -> None:
    """
    Archive a project by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to archive.
    """
    await update_project(client, session, project_id, {'archived': True})

async def unarchive_project(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId) -> None:
    """
    Unarchive a project by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to unarchive.
    """
    await update_project(client, session, project_id, {'archived': False})


async def get_owned_projects(
    client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId
) -> list[Project]:
    """
    Retrieve all projects owned by a specific user.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        user_id: ObjectId of the user whose projects are being retrieved.
    Returns:
        A list of Project instances representing the projects owned by the user.
    """
    cursor = client[DATABASE][PROJECTS_COLLECTION].find({'owner': user_id}, session=session)
    projects = [Project(**doc) for doc in await cursor.to_list(None)]
    return projects


async def update_slug(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, slug: str) -> None:
    """
    Update a project slug by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to unarchive.
        slug: New project slug
    """
    await update_project(client, session, project_id, {'slug': slug})


async def update_description(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, description: str) -> None:
    """
    Update a project description by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to unarchive.
        description: New project description
    """
    await update_project(client, session, project_id, {'description': description})


async def update_owner(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, owner_id: ObjectId) -> None:
    """
    Update a project owner by its ObjectId.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to unarchive.
        owner_id: New project owner
    """
    await update_project(client, session, project_id, {'owner': owner_id})


async def is_user_owner(
    client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, user_id: ObjectId
) -> bool:
    """
    Check if a user is the owner of a specific project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project to check.
        user_id: ObjectId of the user to check for ownership.
    Returns:
        bool: True if the user is the owner of the project, False otherwise.
    """ 
    project = await find_project(client, session, project_id)
    if not project:
        return False  # or handle the situation where the project is not found
    return project.owner == user_id