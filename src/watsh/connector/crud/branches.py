from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from pymongo.errors import DuplicateKeyError

from src.watsh.lib.exceptions import BranchNotFound, BranchSlugTaken
from src.watsh.lib.models import Branch
from .collections import DATABASE, BRANCHES_COLLECTION

async def create_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    slug: str, 
    default: bool,
) -> ObjectId:
    """
    Create a new branch within a project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
    Returns:
        ObjectId of the newly created branch.
    """
    branch = Branch(project=project_id, environment=environment_id, slug=slug, default=default)
    try:
        result = await client[DATABASE][BRANCHES_COLLECTION].insert_one(
            branch.model_dump(exclude_none=True, by_alias=True), session=session
        )
        return result.inserted_id
    except DuplicateKeyError:
        raise BranchSlugTaken()
        

async def get_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId
) -> Branch:
    """
    Retrieve a specific branch by its ObjectId within a project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
    Returns:
        Branch instance.
    Raises:
        NotFoundException: If the branch is not found.
    """
    doc = await client[DATABASE][BRANCHES_COLLECTION].find_one(
        {'_id': branch_id, 'project': project_id, 'environment': environment_id},
        session=session
    )
    if not doc:
        raise BranchNotFound()
    return Branch(**doc)

async def get_default_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId
) -> Branch:
    """
    Retrieve the default branch for a given project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
    Returns:
        Branch instance representing the default branch.
    Raises:
        NotFoundException: If no default branch is found.
    """
    doc = await client[DATABASE][BRANCHES_COLLECTION].find_one(
        {'default': True, 'project': project_id, 'environment': environment_id},
        session=session
    )
    if not doc:
        raise RuntimeError('Default branch not found.')
    return Branch(**doc)

async def list_branches_per_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId
) -> list[Branch]:
    """
    List all branches within a specific project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
    Returns:
        List of Branch instances.
    """
    cursor = client[DATABASE][BRANCHES_COLLECTION].find(
        {'project': project_id, 'environment': environment_id},
        session=session
    )
    return [Branch(**doc) for doc in await cursor.to_list(None)]


async def update_branch_attribute(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    attribute: str, 
    value
) -> None:
    """
    Update a specific attribute of a branch.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        attribute: Name of the attribute to update.
        value: New value for the attribute.
    Raises:
        DuplicateException: If the update causes a duplicate slug.
    """
    try:
        await client[DATABASE][BRANCHES_COLLECTION].update_one(
            {'_id': branch_id, 'project': project_id, 'environment': environment_id},
            {'$set': {attribute: value}},
            session=session
        )
    except DuplicateKeyError:
        raise BranchSlugTaken()

async def update_slug(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
                     environment_id: ObjectId, branch_id: ObjectId, slug: str) -> None:
    await update_branch_attribute(client, session, project_id, environment_id, branch_id, 'slug', slug)

# async def archive_branch(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
#                          environment_id: ObjectId, branch_id: ObjectId) -> None:
#     await update_branch_attribute(client, session, project_id, environment_id, branch_id, 'archived', True)

# async def unarchive_branch(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
#                            environment_id: ObjectId, branch_id: ObjectId) -> None:
#     await update_branch_attribute(client, session, project_id, environment_id, branch_id, 'archived', False)

async def update_default(client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId, 
                         environment_id: ObjectId, branch_id: ObjectId, default: bool) -> None:
    await update_branch_attribute(client, session, project_id, environment_id, branch_id, 'default', default)


async def delete_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId
) -> None:
    """
    Delete a specific branch from a project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch to be deleted.
    """
    result = await client[DATABASE][BRANCHES_COLLECTION].delete_one(
        {'_id': branch_id, 'project': project_id, 'environment': environment_id}, 
        session=session
    )

    if result.deleted_count == 0:
        raise BranchNotFound()


async def check_branch_exists(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId
) -> bool:
    """
    Check if a specific branch exists within a project environment in MongoDB.

    Args:
        client (AgnosticClient): MongoDB client.
        session (AgnosticClientSession): MongoDB client session.
        project_id (ObjectId): ObjectId of the project.
        environment_id (ObjectId): ObjectId of the environment.
        branch_id (ObjectId): ObjectId of the branch.

    Returns:
        bool: True if the branch exists, False otherwise.
    """
    doc = await client[DATABASE][BRANCHES_COLLECTION].find_one(
        {'_id': branch_id, 'project': project_id, 'environment': environment_id},
        session=session
    )
    return doc is not None