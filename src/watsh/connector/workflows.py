from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession

from .crud import (
    users as crud_users, projects as crud_projects, members as crud_members, items as crud_items,
    environments as crud_environments, branches as crud_branches, commits as crud_commits,   
)


async def create_user(
    client: AgnosticClient, session: AgnosticClientSession, email_address: str, 
    create_sample_project: bool = True
) -> ObjectId:
    user_id = await crud_users.create_user(client, session, email_address)

    if create_sample_project:
        await create_project(
            client=client,
            session=session,
            slug='example-project',
            description='This is your first project',
            owner=user_id,
        )

    return user_id


async def create_project(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    slug: str,
    description: str,
    owner: ObjectId,
    create_sample_environments: bool = True,
) -> ObjectId:
    project_id = await crud_projects.create_project(client, session, slug, description, owner)
   
    await crud_members.create_member(
        client=client, 
        session=session, 
        user_id=owner, 
        project_id=project_id
    )
        
    if create_sample_environments:
        await create_environment(
            client=client,
            session=session,
            project_id=project_id,
            slug='production',
            default=True
        )

        await create_environment(
            client=client,
            session=session,
            project_id=project_id,
            slug='development',
            default=False
        )

        await create_environment(
            client=client,
            session=session,
            project_id=project_id,
            slug='staging',
            default=False
        )
        
    return project_id


async def create_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    slug: str,
    default: bool,
) -> ObjectId:
    environment_id = await crud_environments.create_environment(
        client=client, session=session, project_id=project_id, slug=slug, default=default,
    )
    
    await crud_branches.create_branch(
        client=client, session=session, project_id=project_id, environment_id=environment_id,
        slug='main', default=True,
    )
    
    return environment_id


async def delete_user(
    client: AgnosticClient, session: AgnosticClientSession, user_id: ObjectId
) -> None:
    list_projects = await crud_projects.get_owned_projects(
        client=client,
        session=session,
        user_id=user_id
    )

    for project in list_projects:
        await delete_project(
            client=client,
            session=session,
            project_id=project.id,
        )

    await crud_users.delete_user(client, session, user_id)
    

async def delete_project(
    client: AgnosticClient, session: AgnosticClientSession, project_id: ObjectId
) -> None:
    list_environments = await crud_environments.list_environments_per_project(
        client=client,
        session=session,
        project_id=project_id,
    )

    for environment in list_environments:
        await delete_environment(
            client=client,
            session=session,
            project_id=project_id,
            environment_id=environment.id,
        )

    list_members = await crud_members.list_project_members(
        client=client,
        session=session,
        project_id=project_id,
    )

    for member in list_members:
        await crud_members.delete_member(
            client=client,
            session=session,
            user_id=member.user,
            project_id=project_id
        )

    await crud_projects.delete_project(client, session, project_id)



async def delete_environment(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
) -> None:
    list_branches = await crud_branches.list_branches_per_environment(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id
    )

    for branch in list_branches:
        await delete_branch(
            client=client,
            session=session,
            project_id=project_id,
            environment_id=environment_id,
            branch_id=branch.id
        )

    await crud_environments.delete_environment(
        client=client, session=session, project_id=project_id, environment_id=environment_id
    )


async def delete_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> None:
    # Delete commits
    for commit in await crud_commits.list_commits(
        client=client, session=session, project_id=project_id, environment_id=environment_id,
        branch_id=branch_id,
    ):
        await crud_commits.delete_commit(
            client=client, session=session, project_id=project_id, environment_id=environment_id,
            branch_id=branch_id, commit_id=commit.id
        )

    # Delete items
    await crud_items.delete_item_per_branch(
        client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id
    )

    # Delete branch
    await crud_branches.delete_branch(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id
    )

