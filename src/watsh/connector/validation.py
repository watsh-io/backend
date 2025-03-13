from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession

from .crud import environments as crud_environments, branches as crud_branches, projects as crud_projects
from src.watsh.lib.exceptions import BadRequest
from src.watsh.lib.models import Project, Branch, Environment


async def project_validation(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId,
    check_is_not_archive: bool = False
) -> Project:
    project = await crud_projects.find_project(
        client=client, session=session, project_id=project_id
    )

    if check_is_not_archive and project.archived:
        raise BadRequest('Project is archived.')

    return project


async def environment_validation(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
) -> Environment:
    return await crud_environments.get_environment(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id
    )


async def branch_validation(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> Branch:
    return await crud_branches.get_branch(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id
    )