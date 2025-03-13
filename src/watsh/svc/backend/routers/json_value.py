from fastapi import APIRouter, Depends
from motor.core import AgnosticClient
from bson import ObjectId

from src.watsh.connector import json_value as conn_json
from src.watsh.lib.models import User
from ..authentication import get_current_user
from ..client import get_client
from ..config import AES_SECRET

router = APIRouter(prefix="/json", tags=["json"])


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


@router.get('/{project_id}/{environment_id}/{branch_id}')
async def get_json(common_params: dict = Depends(common_dependency)) -> dict:
    return await conn_json.get_json(aes_password=AES_SECRET, **common_params)


@router.patch('/{project_id}/{environment_id}/{branch_id}')
async def patch_json(common_params: dict = Depends(common_dependency)) -> dict:
    # TODO: patch with json values only
    ...


@router.get('/{project_id}/{environment_id}/{branch_id}/{commit_id}')
async def get_json(commit_id: str, common_params: dict = Depends(common_dependency)) -> dict:
    return await conn_json.get_json_per_commit(commit_id=ObjectId(commit_id), aes_password=AES_SECRET, **common_params)