from motor.core import AgnosticClient
from pymongo import ASCENDING

from .crud.collections import (
    DATABASE,
    USERS_COLLECTION,
    PROJECTS_COLLECTION,
    MEMBERS_COLLECTION,
    ENVIRONMENTS_COLLECTION,
    BRANCHES_COLLECTION,
    # ITEMS_COLLECTION,
    COMMITS_COLLECTION,
)


async def create_indexes(client: AgnosticClient) -> None:
    """
    Create necessary indexes for collections in the MongoDB database.
    
    Args:
        client (AgnosticClient): The Motor client for asynchronous operations with MongoDB.
    """
    db = client[DATABASE]

    # Unique index for user emails
    await db[USERS_COLLECTION].create_index('email', unique=True)

    # Unique compound index for projects, combining slug and owner
    await db[PROJECTS_COLLECTION].create_index(
        [('slug', ASCENDING), ('owner', ASCENDING)], unique=True
    )

    # Unique compound index for members, combining user and project
    await db[MEMBERS_COLLECTION].create_index(
        [('user', ASCENDING), ('project', ASCENDING)], unique=True
    )

    # Unique compound index for environments, combining project and slug
    await db[ENVIRONMENTS_COLLECTION].create_index(
        [('project', ASCENDING), ('slug', ASCENDING)], unique=True
    )

    # Unique compound index for branches, ensuring unique slugs within each environment and project combination
    await db[BRANCHES_COLLECTION].create_index(
        [("environment", ASCENDING), ("project", ASCENDING), ("slug", ASCENDING)], 
        unique=True
    )

    # Partial unique index for branches where root is true
    await db[BRANCHES_COLLECTION].create_index(
        [("project", ASCENDING), ("environment", ASCENDING), ("default", ASCENDING)],
        unique=True,
        partialFilterExpression={"default": True}
    )

    # Unique compound index for commit, ensuring commit ordering
    await db[COMMITS_COLLECTION].create_index(
        [
            ('project', ASCENDING),
            ('environment', ASCENDING),
            ('branch', ASCENDING),
            ('timestamp', ASCENDING), 
        ], 
        unique=True,
    )


# TODO: validate configuration for High Availability with a 'settings' collection
