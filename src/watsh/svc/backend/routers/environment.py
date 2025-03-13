from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Query, Response

from src.watsh.connector import environments as conn_environments
from src.watsh.lib.models import User, Environment, ObjectIDResponse
from ..authentication import get_current_user
from ..client import get_client
from ..config import MAX_SLUG_LEN, MIN_SLUG_LEN, SLUG_REGEX

router = APIRouter(prefix="/environment", tags=["environment"])


@router.get('/{project_id}')
async def get_environments(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> list[Environment]:
    return await conn_environments.list_environments(
        client=client, current_user_id=current_user.id, project_id=ObjectId(project_id)
    )


@router.get('/{project_id}/{environment_id}')
async def get_environment(
    project_id: str, environment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> Environment:
    return await conn_environments.get(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id)
    )


@router.delete('/{project_id}/{environment_id}')
async def delete_environment(
    project_id: str, environment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_environments.delete(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id)
    )
    return Response(status_code=status.HTTP_200_OK)

@router.post('/{project_id}', status_code=status.HTTP_201_CREATED)
async def create_environment(
    project_id: str, 
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)],  
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> ObjectIDResponse:
    environment_id = await conn_environments.create(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        slug=slug,
    )    
    return ObjectIDResponse(id=environment_id)


@router.patch('/{project_id}/{environment_id}/slug')
async def patch_slug(
    project_id: str, environment_id: str, slug: str, 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_environments.slug_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        slug=slug,
    )
    return Response(status_code=status.HTTP_200_OK)

@router.patch('/{project_id}/{environment_id}/default')
async def patch_default(
    project_id: str, environment_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_environments.default_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
    )
    return Response(status_code=status.HTTP_200_OK)

# @router.patch('/{project_id}/{environment_id}/archive')
# async def patch_archive(
#     project_id: str, environment_id: str,
#     current_user: Annotated[User, Depends(get_current_user)],
#     client: AgnosticClient = Depends(get_client),
# ) -> None:
#     project_id = await conn_environments.archive_environment(
#         client=client, 
#         current_user_id=current_user.id, 
#         project_id=ObjectId(project_id),
#         environment_id=ObjectId(environment_id),
#     )

# @router.patch('/{project_id}/{environment_id}/unarchive')
# async def patch_unarchive(
#     project_id: str, environment_id: str,
#     current_user: Annotated[User, Depends(get_current_user)],
#     client: AgnosticClient = Depends(get_client),
# ) -> None:
#     project_id = await conn_environments.unarchive_environment(
#         client=client, 
#         current_user_id=current_user.id, 
#         project_id=ObjectId(project_id),
#         environment_id=ObjectId(environment_id),
#     )