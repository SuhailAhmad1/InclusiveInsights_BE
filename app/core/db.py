import logging
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.server_api import ServerApi
from config import DB_URI
import logging

# Suppress PyMongo logs

uri = DB_URI

client: AsyncIOMotorClient | None = None


def connect_to_mongo():
    global client
    client = AsyncIOMotorClient(
        DB_URI,
        server_api=ServerApi("1")
    )


def close_mongo_connection():
    if client:
        client.close()


def get_db():
    if client is None:
        raise RuntimeError("MongoDB client is not initialized")
    return client["InclusiveInsights"]
