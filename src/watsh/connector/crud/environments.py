from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from src.watsh.lib.exceptions import EnvironmentNotFound, EnvironmentSlugTaken
from src.watsh.lib.models import Environment
from .collections import DATABASE, ENVIRONMENTS_COLLECTION

async def create_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    slug: str, 
    default: bool,
) -> ObjectId:
    """
    Create a new environment within a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        slug: Unique slug for the environment.
    Returns:
        ObjectId of the newly created environment.
    Raises:
        EnvironmentSlugTaken: If an environment with the same slug already exists.
    """
    environment = Environment(project=project_id, slug=slug, default=default)
    try:
        result = await client[DATABASE][ENVIRONMENTS_COLLECTION].insert_one(
            environment.model_dump(exclude_none=True, by_alias=True), session=session
        )
        return result.inserted_id
    except DuplicateKeyError:
        raise EnvironmentSlugTaken()

async def get_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId
) -> Environment:
    """
    Retrieve a specific environment by its ObjectId within a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
    Returns:
        Environment instance.
    Raises:
        EnvironmentNotFound: If the environment is not found.
    """
    doc = await client[DATABASE][ENVIRONMENTS_COLLECTION].find_one(
        {'_id': environment_id, 'project': project_id}, session=session
    )
    if not doc:
        raise EnvironmentNotFound()
    return Environment(**doc)


async def get_default_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
) -> Environment:
    """
    Retrieve the default environment by its ObjectId within a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
    Returns:
        Environment instance.
    Raises:
        EnvironmentNotFound: If the environment is not found.
    """
    doc = await client[DATABASE][ENVIRONMENTS_COLLECTION].find_one(
        {'default': True, 'project': project_id}, session=session
    )
    if not doc:
        raise EnvironmentNotFound()
    return Environment(**doc)


async def list_environments_per_project(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId
) -> list[Environment]:
    """
    List all environments belonging to a specific project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
    Returns:
        List of Environment instances.
    """
    cursor = client[DATABASE][ENVIRONMENTS_COLLECTION].find({'project': project_id}, session=session)
    return [Environment(**doc) for doc in await cursor.to_list(None)]

async def delete_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId
) -> None:
    """
    Delete an environment from a project.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment to delete.
    """
    result = await client[DATABASE][ENVIRONMENTS_COLLECTION].delete_one(
        {'_id': environment_id, 'project': project_id}, session=session
    )

    if not result.deleted_count:
        raise EnvironmentNotFound()

async def update_environment_attribute(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    attribute: str, 
    value
) -> None:
    """
    Update a specific attribute of an environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        attribute: Name of the attribute to update.
        value: New value for the attribute.
    Raises:
        EnvironmentSlugTaken: If the update causes a duplicate slug.
    """
    try:
        await client[DATABASE][ENVIRONMENTS_COLLECTION].update_one(
            {'_id': environment_id, 'project': project_id},
            {'$set': {attribute: value}},
            session=session
        )
    except DuplicateKeyError:
        raise EnvironmentSlugTaken()

async def update_slug(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
                      environment_id: ObjectId, slug: str) -> None:
    await update_environment_attribute(client, session, project_id, environment_id, 'slug', slug)

async def update_default(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
                    environment_id: ObjectId, default: bool) -> None:
    await update_environment_attribute(client, session, project_id, environment_id, 'default', default)

# async def archive_environment(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
#                               environment_id: ObjectId) -> None:
#     await update_environment_attribute(client, session, project_id, environment_id, 'archived', True)

# async def unarchive_environment(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
#                                 environment_id: ObjectId) -> None:
#     await update_environment_attribute(client, session, project_id, environment_id, 'archived', False)

async def default_environment(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
                                environment_id: ObjectId, default: bool) -> None:
    await update_environment_attribute(client, session, project_id, environment_id, 'default', default)

async def check_environment_exists(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId
) -> bool:
    """
    Check if a specific environment exists within a project in MongoDB.

    Args:
        client (AgnosticClient): MongoDB client.
        session (AgnosticClientSession): MongoDB client session.
        project_id (ObjectId): ObjectId of the project.
        environment_id (ObjectId): ObjectId of the environment.

    Returns:
        bool: True if the environment exists, False otherwise.
    """
    doc = await client[DATABASE][ENVIRONMENTS_COLLECTION].find_one(
        {'_id': environment_id, 'project': project_id}, session=session
    )
    return doc is not None