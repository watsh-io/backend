from motor.core import AgnosticClient
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi

from src.watsh.connector import setup
from .config import MONGO_URI

client = AsyncIOMotorClient(MONGO_URI, server_api=ServerApi('1'))


async def setup_indexes() -> None:
    global client
    await setup.create_indexes(client)


async def close_client() -> None:
    global client
    try:
        await client.close()
    except TypeError:
        pass


async def get_client() -> AgnosticClient:
    global client
    return client