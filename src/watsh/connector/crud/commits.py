from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession

from src.watsh.lib.exceptions import CommitNotFound
from src.watsh.lib.models import Commit
from .collections import DATABASE, COMMITS_COLLECTION

async def get_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_id: ObjectId
) -> Commit:
    """
    Retrieve a specific commit from a project's branch in an environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        commit_id: ObjectId of the commit to retrieve.
    Returns:
        Commit instance.
    Raises:
        NotFoundException: If the specified commit is not found.
    """
    query = {
        '_id': commit_id,
        'project': project_id,
        'environment': environment_id,
        'branch': branch_id
    }
    doc = await client[DATABASE][COMMITS_COLLECTION].find_one(query, session=session)
    if not doc:
        raise CommitNotFound()
    return Commit(**doc)

async def list_commits(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId
) -> list[Commit]:
    """
    List all commits for a given branch within a project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
    Returns:
        List of Commit instances.
    """
    cursor = client[DATABASE][COMMITS_COLLECTION].find(
        {'project': project_id, 'environment': environment_id, 'branch': branch_id},
        session=session
    )
    return [Commit(**doc) for doc in await cursor.to_list(None)]

async def create_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    current_user_id: ObjectId,
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_message: str,
    timestamp: int
) -> ObjectId:
    """
    Create a new commit in a branch within a project environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        current_user_id: ObjectId of the user creating the commit.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        commit_message: Message associated with the commit.
        timestamp: Timestamp of the commit.
    Returns:
        ObjectId of the newly created commit.
    """
    commit = Commit(
        project=project_id, environment=environment_id, branch=branch_id,
        author=current_user_id, message=commit_message, timestamp=timestamp
    )
    result = await client[DATABASE][COMMITS_COLLECTION].insert_one(
        commit.model_dump(exclude_none=True, by_alias=True), session=session
    )
    return result.inserted_id



async def delete_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_id: ObjectId
) -> None:
    """
    Delete a specific commit from a project's branch in an environment.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        commit_id: ObjectId of the commit to delete.
    Returns:
        None
    Raises:
        NotFoundException: If the specified commit is not found.
    """
    query = {
        '_id': commit_id,
        'project': project_id,
        'environment': environment_id,
        'branch': branch_id
    }
    doc = await client[DATABASE][COMMITS_COLLECTION].delete_one(query, session=session)
    if not doc.deleted_count:
        raise CommitNotFound()
