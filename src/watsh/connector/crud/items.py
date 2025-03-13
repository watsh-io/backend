from bson import ObjectId
from motor.core import AgnosticClient, AgnosticClientSession
from typing import Any

from .collections import DATABASE, ITEMS_COLLECTION
from src.watsh.lib.models import Item, ItemType
from src.watsh.lib.exceptions import ItemNotFound

async def _aggregate_items(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    match_stage: dict
) -> list[Item]:
    """
    Helper function to aggregate items based on a given match stage.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        match_stage: Match stage for the aggregation pipeline.
    Returns:
        List of Item instances.
    """
    sort_stage = {"$sort": {"timestamp": -1}}
    group_stage = {
        "$group": {
            "_id": "$item",
            "item": {"$first": "$$ROOT"},
        }
    }
    replace_root_stage = {"$replaceRoot": {"newRoot": "$item"}}
    filter_active_stage = {"$match": {"active": True}}
    sort_slug_stage = {"$sort": {"slug": 1}}
    pipeline = [match_stage, sort_stage, group_stage, replace_root_stage, filter_active_stage, sort_slug_stage]
    cursor = client[DATABASE][ITEMS_COLLECTION].aggregate(pipeline, session=session)
    
    return [Item(**doc) for doc in await cursor.to_list(None)]

async def list_items_per_commit(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    commit_timestamp: int
) -> list[Item]:
    """
    List items for a project environment's branch at or before a specific commit timestamp.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        commit_timestamp: The timestamp of the commit.
    Returns:
        List of Item instances.
    """
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'timestamp': {'$lte': commit_timestamp}
        }
    }
    return await _aggregate_items(client, session, match_stage)

async def list_items_per_commit_per_parent(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    commit_timestamp: int
) -> list[Item]:
    """
    List items for a project environment's branch at or before a specific commit timestamp, filtered by parent.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        parent_id: ObjectId of the parent item.
        commit_timestamp: The timestamp of the commit.
    Returns:
        List of Item instances.
    """
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'parent': parent_id,
            'timestamp': {'$lte': commit_timestamp}
        }
    }
    return await _aggregate_items(client, session, match_stage)

async def create_item(
    client: AgnosticClient, session: AgnosticClientSession, 
    project_id: ObjectId, environment_id: ObjectId, branch_id: ObjectId, 
    parent_id: ObjectId, item_id: ObjectId, item_slug: str | None, item_type: ItemType, item_active: bool, 
    secret_value: Any, secret_active: bool, commit_id: ObjectId, timestamp: int
) -> ObjectId:
    item = Item(
        project=project_id, environment=environment_id, branch=branch_id, 
        item=item_id, parent=parent_id, slug=item_slug, type=item_type,
        active=item_active, secret_value=secret_value, secret_active=secret_active, commit=commit_id, timestamp=timestamp
    )
    result = await client[DATABASE][ITEMS_COLLECTION].insert_one(
        item.model_dump(exclude_none=True, by_alias=True), session=session
    )
    return result.inserted_id

async def delete_item(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId,
) -> None:
    """
    Delete a all items on a project environment's branch.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        item_id: ObjectId of the item.
    Returns:
        None
    """
    query = {
        "project": project_id,
        "environment": environment_id,
        'branch': branch_id,
        'item': item_id
    }
    await client[DATABASE][ITEMS_COLLECTION].delete_many(query, session=session)

async def delete_item_per_branch(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> None:
    """
    Delete a all items on a project environment's branch.
    Args:
        client: MongoDB client.
        session: MongoDB client session.
        project_id: ObjectId of the project.
        environment_id: ObjectId of the environment.
        branch_id: ObjectId of the branch.
        item_id: ObjectId of the item.
    Returns:
        None
    """
    query = {
        "project": project_id,
        "environment": environment_id,
        'branch': branch_id,
    }
    await client[DATABASE][ITEMS_COLLECTION].delete_many(query, session=session)


async def list_items(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
) -> list[Item]:
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'timestamp': {'$lte': 9999999999999999}
        }
    }
    return await _aggregate_items(client, session, match_stage)

async def list_items_per_parent(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
) -> list[Item]:
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'parent': parent_id,
            'timestamp': {'$lte': 9999999999999999}
        }
    }
    return await _aggregate_items(client, session, match_stage)

async def get_item(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    item_id: ObjectId
) -> Item:
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'item': item_id,
            'timestamp': {'$lte': 9999999999999999}
        }
    }
    items = await _aggregate_items(client, session, match_stage)
    if len(items) > 1:
        raise RuntimeError('More than 1 item returned.')
    if len(items) == 0:
        raise ItemNotFound()
    return items[0]



async def get_item_by_slug(
    client: AgnosticClient, 
    session: AgnosticClientSession, 
    project_id: ObjectId, 
    environment_id: ObjectId,
    branch_id: ObjectId,
    parent_id: ObjectId,
    slug: str
) -> Item:
    match_stage = {
        "$match": {
            "project": project_id,
            "environment": environment_id,
            'branch': branch_id,
            'timestamp': {'$lte': 9999999999999999}
        }
    }
    sort_stage = {"$sort": {"timestamp": -1}}
    group_stage = {
        "$group": {
            "_id": "$item",
            "item": {"$first": "$$ROOT"},
        }
    }
    replace_root_stage = {"$replaceRoot": {"newRoot": "$item"}}
    filter_active_stage = {"$match": {"active": True, "slug": slug, "parent": parent_id}}
    sort_slug_stage = {"$sort": {"slug": 1}}
    pipeline = [match_stage, sort_stage, group_stage, replace_root_stage, filter_active_stage, sort_slug_stage]
    cursor = client[DATABASE][ITEMS_COLLECTION].aggregate(pipeline, session=session)
    
    items = [Item(**doc) for doc in await cursor.to_list(None)]
    if len(items) > 1:
        raise RuntimeError('More than 1 item returned.')
    if len(items) == 0:
        raise ItemNotFound()
    return items[0]