import os
import re
import json
from bson import ObjectId
from typing import Annotated
from motor.core import AgnosticClient
from fastapi import APIRouter, status, Depends, Body
from fastapi.responses import HTMLResponse, FileResponse
from json_schema_for_humans.generate import generate_from_file_object

from src.watsh.connector import schema as conn_schema
from src.watsh.lib.models import User

from ..authentication import get_current_user
from ..client import get_client


router = APIRouter(prefix="/schema", tags=["schema"])


@router.get('/{project_id}/{environment_id}/{branch_id}', status_code=status.HTTP_200_OK)
async def get_schema(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> dict:
    return await conn_schema.get_schema(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
    )

@router.post('/{project_id}/{environment_id}/{branch_id}/generate', status_code=status.HTTP_200_OK)
async def generate(
    project_id: str, environment_id: str, branch_id: str,
    data: Annotated[dict, Body()],
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> dict:
    return await conn_schema.generate(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
        data=data
    )


@router.get('/{project_id}/{environment_id}/{branch_id}/docs')
async def get_schema_docs(
    project_id: str, environment_id: str, branch_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> FileResponse:
    schema_dict = await conn_schema.get_schema(
        client=client, 
        current_user_id=current_user.id, 
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
    )

    # Generate a temporary id
    schema_id = str(ObjectId())
    schema_name = f'{schema_id}.json'
    schema_html = f'{schema_id}.html'

    with open(schema_name, 'w') as f:
        json.dump(schema_dict, f)
        f.close()
    
    # Generate doc
    with open(schema_name) as f:
        with open(schema_html, 'w') as f2:
            generate_from_file_object(schema_file=f, result_file=f2)
            f2.close()
        
        with open(schema_html) as f2:
            html_content = f2.read()
            f2.close()
        f.close()

    os.remove(schema_name)
    os.remove(schema_html)
    os.remove('schema_doc.css')
    os.remove('schema_doc.min.js')

    pattern = re.compile(r'<footer>.*?</footer>', re.DOTALL)
    modified_content = re.sub(pattern, '', html_content)
    return HTMLResponse(modified_content)


@router.get('/{project_id}/{environment_id}/{branch_id}/{commit_id}')
async def get_schema(
    project_id: str, environment_id: str, branch_id: str, commit_id: str,
    current_user: Annotated[User, Depends(get_current_user)],
    client: AgnosticClient = Depends(get_client),
) -> dict:
    return await conn_schema.get_schema_per_commit(
        client=client, 
        current_user_id=current_user.id,
        project_id=ObjectId(project_id),
        environment_id=ObjectId(environment_id),
        branch_id=ObjectId(branch_id),
        commit_id=ObjectId(commit_id),
    )
