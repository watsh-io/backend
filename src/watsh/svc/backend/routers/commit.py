from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, Depends, status

from src.watsh.connector import commits as conn_commits, items as conn_items
from src.watsh.lib.models import User, Commit, Item
from ..authentication import get_current_user
from ..client import get_client
from ..config import AES_SECRET


router = APIRouter(prefix="/commit", tags=["commit"])


@router.get('/{project_id}/{environment_id}/{branch_id}')
async def get_commits(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> list[Commit]:
    return await conn_commits.list_commits(
        client=client, 
        current_user_id=current_user.id,
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
    )



@router.get(
    '/{project_id}/{environment_id}/{branch_id}/{commit_id}',
    response_model=list[Item],
    status_code=status.HTTP_200_OK
)
async def get_items(
    project_id: str, environment_id: str, branch_id: str, commit_id: str,
    current_user: User = Depends(get_current_user),
    client: AgnosticClient = Depends(get_client),
) -> list[Item]:
    """
    Get snapshots for a given project, environment, and branch, at a given commit ID

    Parameters:
    - project_id: string ID of the project.
    - environment_id: string ID of the environment.
    - branch_id: string ID of the branch.
    - commit_id: string ID of the commit
    - current_user: Current authenticated user.
    - client: MongoDB client.

    Returns:
    - list[Snapshot]: List of Snapshot instances.
    """
    return await conn_items.list_items_per_commit(
        client=client,
        current_user_id=current_user.id,
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
        commit_id=ObjectId(commit_id),
        aes_password=AES_SECRET,
    )


