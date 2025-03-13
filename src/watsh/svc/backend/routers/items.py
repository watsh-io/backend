from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Body, Query
from pydantic import BaseModel, validator
from bson import ObjectId

from src.watsh.lib.pyobjectid import PyObjectId
from src.watsh.connector import items as conn_items
from src.watsh.lib.models import User, ObjectIDResponse, Item, ItemUpdate
from ..authentication import get_current_user
from ..client import get_client
from ..config import MAX_SLUG_LEN, MIN_SLUG_LEN, SLUG_REGEX, AES_SECRET

router = APIRouter(prefix="/items", tags=["items"])


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
        

class ItemUpdateRequest(ItemUpdate):
    slug: Annotated[str, Query(min_length=MIN_SLUG_LEN, max_length=MAX_SLUG_LEN, regex=SLUG_REGEX)]

    @validator("item", "parent", pre=True, allow_reuse=True)
    def validate_object_id(cls, value):
        if isinstance(value, PyObjectId):
            return value
        if isinstance(value, str) and PyObjectId.validate(value):
            return PyObjectId(value)
        raise ValueError("Invalid ObjectId")
    

@router.patch('/{project_id}/{environment_id}/{branch_id}')
async def patch_items(
    data: Annotated[list[ItemUpdateRequest], Body()],
    common_params: dict = Depends(common_dependency),
    commit_message: str = 'Snapshot commit.',
) -> ObjectIDResponse:
    commit_id = await conn_items.create_from_updates(
        updates=data, commit_message=commit_message, aes_password=AES_SECRET, **common_params
    )
    return ObjectIDResponse(id=commit_id)

    
class PatchItem(BaseModel):
    json_schema: dict
    json_value: dict


@router.patch('/{project_id}/{environment_id}/{branch_id}/json')
async def patch_snapshot(
    data: Annotated[PatchItem, Body()],
    common_params: dict = Depends(common_dependency),
    commit_message: str = 'Snapshot commit',
) -> ObjectIDResponse:
    commit_id = await conn_items.create_from_schema(
        json_schema=data.json_schema, json_values=data.json_value, 
        commit_message=commit_message, aes_password=AES_SECRET, **common_params
    )
    return ObjectIDResponse(id=commit_id)
