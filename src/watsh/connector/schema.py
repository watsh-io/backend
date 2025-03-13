from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from genson import SchemaBuilder
from jsonschema import protocols

from . import access_control, validation, schema
from .crud import projects as crud_projects, commits as crud_commits, items as crud_items
from src.watsh.lib.models import Project, ItemType
from src.watsh.lib.pyobjectid import NULL_OBJECTID



def build_schema(schema_id: str, project: Project, properties: dict) -> dict:
    return {
        "$schema": "https://json-schema.org/draft/2020-12/schema",
        "$id": schema_id,
        "title": project.slug,
        "description": project.description,
        "type": "object",
        "properties": properties
    }


async def get_properties(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
) -> dict:
    
    items = await crud_items.list_items_per_parent(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
        parent_id=parent_id,
    )

    result = {}
    
    for item in items:
        
        if item.type == ItemType.OBJECT.value:
            result[item.slug] = {'type': item.type}
            result[item.slug]['properties'] = await get_properties(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=item.item
            )

        # elif item.type == ItemType.ARRAY.value:
        #     """NOTE: arrays are an abastraction. 
        #     They are converted back into objects, with each slug
        #     being dynamically generated as an increasing integer.
        #     """
        #     result[item.slug] = {'type': item.type}
        #     result[item.slug]['properties'] = await get_properties(
        #         client=client,
        #         session=session,
        #         project_id=project_id,
        #         environment_id=environment_id,
        #         branch_id=branch_id,
        #         parent_id=item.item
        #     )
        else:
            result[item.slug] = {'type': item.type}

    return result


async def get_schema(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> dict:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get project
            project = await crud_projects.find_project(
                client=client, session=session, project_id=project_id
            )

            # Get properties
            properties = await get_properties(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=NULL_OBJECTID,
            )

            # Commit the transaction
            await session.commit_transaction()

    schema_id = f"https://api.watsh.io/v1/schema/{project_id}/{environment_id}/{branch_id}"
    return schema.build_schema(schema_id, project, properties)





async def get_properties_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession,
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    commit_timestamp: int,
) -> dict:
    
    items = await crud_items.list_items_per_commit_per_parent(
        client=client,
        session=session,
        project_id=project_id,
        environment_id=environment_id,
        branch_id=branch_id,
        parent_id=parent_id,
        commit_timestamp=commit_timestamp,
    )

    result = {}
    
    for item in items:
        
        if item.type == ItemType.OBJECT.value:
            result[item.slug] = {'type': item.type}
            result[item.slug]['properties'] = await get_properties_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=item.item,
                commit_timestamp=commit_timestamp,
            )

        # elif item.type == ItemType.ARRAY.value:
        #     """NOTE: arrays are an abastraction. 
        #     They are converted back into objects, with each slug
        #     being dynamically generated as an increasing integer.
        #     """
        #     result[item.slug] = {'type': item.type}
        #     result[item.slug]['properties'] = await get_properties(
        #         client=client,
        #         session=session,
        #         project_id=project_id,
        #         environment_id=environment_id,
        #         branch_id=branch_id,
        #         parent_id=item.item
        #     )
        else:
            result[item.slug] = {'type': item.type}

    return result


async def get_schema_per_commit(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_id: ObjectId,
) -> dict:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get commit
            commit = await crud_commits.get_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                commit_id=commit_id,
            )


            # Get project
            project = await crud_projects.find_project(
                client=client, session=session, project_id=project_id
            )

            # Get properties
            properties = await get_properties_commit(
                client=client,
                session=session,
                project_id=project_id,
                environment_id=environment_id,
                branch_id=branch_id,
                parent_id=NULL_OBJECTID,
                commit_timestamp=commit.timestamp
            )

            # Commit the transaction
            await session.commit_transaction()

    schema_id = f"https://api.watsh.io/v1/schema/{project_id}/{environment_id}/{branch_id}/{commit_id}"
    return schema.build_schema(schema_id, project, properties)


async def generate(
    client: AgnosticClient, 
    current_user_id: ObjectId, 
    project_id: ObjectId,
    environment_id: ObjectId,
    branch_id: ObjectId,
    data: dict,
) -> dict:
    # Start a transaction to ensure that all the inserts are performed atomically.
    async with await client.start_session() as session:
        async with session.start_transaction():
            
            # Access control
            await access_control.user_authorization(
                client=client, session=session, project_id=project_id, user_id=current_user_id
            )

            # Verify environment ID
            await validation.environment_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id,
            )

            # Verify branch ID
            await validation.branch_validation(
                client=client, session=session, project_id=project_id, environment_id=environment_id, branch_id=branch_id, 
            )

            # Get project
            project = await crud_projects.find_project(
                client=client, session=session, project_id=project_id
            )

            # Commit the transaction
            await session.commit_transaction()
    
    # Generate schema
    builder = SchemaBuilder(schema_uri='https://json-schema.org/draft/2020-12/schema#')
    schema_id = f"https://api.watsh.io/v1/schema/{project_id}/{environment_id}/{branch_id}"
    builder.add_schema(
        {
            "$id": schema_id,
            "title": project.slug,
            "description": project.description,
            "type": "object", 
            "properties": {}
        }
    )
    builder.add_object(data)
    generated_schema = dict(builder.to_schema())

    # Check schema is valid
    protocols.Validator.check_schema(generated_schema)

    return generated_schema