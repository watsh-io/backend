from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Response, Query

from src.watsh.connector import items as conn_items
from src.watsh.lib.models import User, ObjectIDResponse, ItemType, Item
from src.watsh.lib.pyobjectid import NULL_OBJECTID
from ..authentication import get_current_user
from ..client import get_client
from ..config import MAX_SLUG_LEN, MIN_SLUG_LEN, SLUG_REGEX, AES_SECRET


router = APIRouter(prefix="/item", tags=["item"])



async def common_dependency(
    project_id: str,
    environment_id: str,
    branch_id: str,
    current_user: User = Depends(get_current_user),
    client: AgnosticClient = Depends(get_client),
) -> dict:
    return {
        "client": client,
        "current_user_id": current_user.id,
        "project_id": ObjectId(project_id),
        "environment_id": ObjectId(environment_id),
        "branch_id": ObjectId(branch_id),
    }


@router.get('/{project_id}/{environment_id}/{branch_id}', status_code=status.HTTP_200_OK)
async def get_items(
    common_params: dict = Depends(common_dependency),
) -> list[Item]:
    return await conn_items.list_items(aes_password=AES_SECRET, **common_params)

@router.get('/{project_id}/{environment_id}/{branch_id}/{item_id}', status_code=status.HTTP_200_OK)
async def get_item(
    item_id: str, common_params: dict = Depends(common_dependency),
) -> Item:
    return await conn_items.get(item_id=ObjectId(item_id), aes_password=AES_SECRET, **common_params)


@router.delete('/{project_id}/{environment_id}/{branch_id}/{item_id}', status_code=status.HTTP_200_OK)
async def delete_item(
    item_id: str, commit_message: str = 'Delete item.', common_params: dict = Depends(common_dependency),
) -> None:
    await conn_items.delete(item_id=ObjectId(item_id), commit_message=commit_message, **common_params)
    return Response(status_code=status.HTTP_200_OK)


@router.post('/{project_id}/{environment_id}/{branch_id}', status_code=status.HTTP_201_CREATED)
async def create_item(
    item_type: ItemType,
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)], 
    parent_id: str = '', 
    commit_message: str = 'Item created.',
    common_params: dict = Depends(common_dependency),
) -> ObjectIDResponse:
    # TODO: add secret value in params
    # TODO: check secret value with type
    # TODO: encrypt secret value
    item_id = await conn_items.create(
        parent_id=NULL_OBJECTID if not parent_id else ObjectId(parent_id),
        item_type=item_type,
        slug=slug,
        commit_message=commit_message,
        secret_active=False,
        secret_value=None,
        aes_password=AES_SECRET,
        **common_params
    )
    return ObjectIDResponse(id=item_id)


@router.patch('/{project_id}/{environment_id}/{branch_id}/{item_id}/slug')
async def patch_slug(
    project_id: str, environment_id: str, branch_id: str, item_id: str, 
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)],  
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
    commit_message: str = 'Slug modified',
) -> None:
    await conn_items.slug_update(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
        item_id=ObjectId(item_id),
        slug=slug,
        commit_message=commit_message,
    )


@router.patch('/{project_id}/{environment_id}/{branch_id}/{item_id}/secret', status_code=status.HTTP_201_CREATED)
async def patch_secret(
    item_id: str, secret: str, commit_message: str = 'Secret created.',
    common_params: dict = Depends(common_dependency),
) -> None:
    await conn_items.create_secret(
        secret=secret, commit_message=commit_message, item_id=ObjectId(item_id), **common_params
    )


@router.delete('/{project_id}/{environment_id}/{branch_id}/{item_id}/secret', status_code=status.HTTP_200_OK)
async def delete_secret(
    item_id: str, commit_message: str = 'Secret deleted.',
    common_params: dict = Depends(common_dependency),
) -> None:
    await conn_items.delete_secret(item_id=ObjectId(item_id), commit_message=commit_message, **common_params)
