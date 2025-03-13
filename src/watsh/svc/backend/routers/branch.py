from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Response, Query

from src.watsh.connector import branches as conn_branches
from src.watsh.lib.models import User, Branch, ObjectIDResponse
from ..authentication import get_current_user
from ..client import get_client
from ..config import MAX_SLUG_LEN, MIN_SLUG_LEN, SLUG_REGEX

router = APIRouter(prefix="/branch", tags=["branch"])


@router.get('/{project_id}/{environment_id}', status_code=status.HTTP_200_OK)
async def get_branches(
    project_id: str, environment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> list[Branch]:
    return await conn_branches.list_branches(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
    )


@router.get('/{project_id}/{environment_id}/{branch_id}', status_code=status.HTTP_200_OK)
async def get_branch(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> Branch:
    return await conn_branches.get(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id)
    )


@router.delete('/{project_id}/{environment_id}/{branch_id}')
async def delete_branch(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_branches.delete(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
    )
    return Response(status_code=status.HTTP_200_OK)

@router.post('/{project_id}/{environment_id}', status_code=status.HTTP_201_CREATED)
async def create_branch(
    project_id: str, environment_id: str, 
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)], 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> ObjectIDResponse:
    branch_id = await conn_branches.create(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        slug=slug,
    )
    return ObjectIDResponse(id=branch_id)


@router.patch('/{project_id}/{environment_id}/{branch_id}/slug')
async def patch_slug(
    project_id: str, environment_id: str, branch_id: str, 
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)], 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_branches.slug_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
        slug=slug,
    )
    return Response(status_code=status.HTTP_200_OK)


# @router.patch('/{project_id}/{environment_id}/{branch_id}/archive')
# async def patch_archive(
#     project_id: str, environment_id: str, branch_id: str,
#     current_user: Annotated[User, Depends(get_current_user)],
#     client: AgnosticClient = Depends(get_client),
# ) -> None:
#     project_id = await conn_branches.archive_update(
#         client=client, 
#         current_user_id=current_user.id, 
#         project_id=ObjectId(project_id),
#         environment_id=ObjectId(environment_id),
#         branch_id=ObjectId(branch_id),
#     )
#     return Response(status_code=status.HTTP_200_OK)


# @router.patch('/{project_id}/{environment_id}/{branch_id}/unarchive')
# async def patch_archive(
#     project_id: str, environment_id: str, branch_id: str,
#     current_user: Annotated[User, Depends(get_current_user)],
#     client: AgnosticClient = Depends(get_client),
# ) -> None:
#     project_id = await conn_branches.unarchive_update(
#         client=client, 
#         current_user_id=current_user.id, 
#         project_id=ObjectId(project_id),
#         environment_id=ObjectId(environment_id),
#         branch_id=ObjectId(branch_id),
#     )
#     return Response(status_code=status.HTTP_200_OK)


@router.patch('/{project_id}/{environment_id}/{branch_id}/default')
async def patch_default(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_branches.default_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
    )
    return Response(status_code=status.HTTP_200_OK)