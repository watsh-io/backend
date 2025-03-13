from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Response, Query

from src.watsh.connector import projects as conn_projects
from src.watsh.lib.models import User, Project, ObjectIDResponse
from ..authentication import get_current_user
from ..client import get_client
from ..config import MAX_DESC_LEN, MAX_SLUG_LEN, MIN_SLUG_LEN, SLUG_REGEX, DESC_REGEX

router = APIRouter(prefix="/project", tags=["project"])



@router.get('', status_code=status.HTTP_200_OK)
async def get_projects(
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> list[Project]:
    return await conn_projects.list_projects(
        client=client, current_user_id=current_user.id
    )


@router.get('/{project_id}', status_code=status.HTTP_200_OK)
async def get_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> Project:
    return await conn_projects.get(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id)
    )


@router.delete('/{project_id}', status_code=status.HTTP_200_OK)
async def delete_project(
    project_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_projects.delete(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id)
    )
    return Response(status_code=status.HTTP_200_OK)


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_project(
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)], 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
    description: Annotated[str, Query(max_length=MAX_DESC_LEN, regex=DESC_REGEX)] = '', 
) -> ObjectIDResponse:
    project_id = await conn_projects.create(
        client=client, 
        current_user_id=current_user.id, 
        slug=slug,
        description=description,
    )
    return ObjectIDResponse(id=project_id)


@router.patch('/{project_id}/slug', status_code=status.HTTP_200_OK)
async def patch_slug(
    project_id: str, 
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)], 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    await conn_projects.slug_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        slug=slug,
    )
    return Response(status_code=status.HTTP_200_OK)

@router.patch('/{project_id}/description', status_code=status.HTTP_200_OK)
async def patch_description(
    project_id: str, 
    description: Annotated[str, Query(max_length=MAX_DESC_LEN, regex=DESC_REGEX)], 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    project_id = await conn_projects.description_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        description=description,
    )
    return Response(status_code=status.HTTP_200_OK)


@router.patch('/{project_id}/archive', status_code=status.HTTP_200_OK)
async def archive_project(
    project_id: str, 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    project_id = await conn_projects.archive_project(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
    )
    return Response(status_code=status.HTTP_200_OK)

@router.patch('/{project_id}/unarchive', status_code=status.HTTP_200_OK)
async def unarchive_project(
    project_id: str, 
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> None:
    project_id = await conn_projects.unarchive_project(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
    )
    return Response(status_code=status.HTTP_200_OK)