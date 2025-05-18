from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI


# Globals to hold the database connection and collections

client = None
_db = None
_users = None
_logs = None


async def init_db():
    """
    Asynchronously initializes the MongoDB connection and sets global database references.
    """
    global client, _db, _users, _logs

    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=50,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            waitQueueTimeoutMS=5000,
        )

        await client.admin.command("ping")
        DB_NAME = "envybase"
        _db = client[DB_NAME]
        _users = _db["users"]
        _logs = _db["logs"]
        print("MongoDB connection established successfully.")
        return True
    except ConnectionFailure as e:
        raise Exception(
            f"Failed to connect to MongoDB: {str(e)}. Please check your connection settings."
        ) from e


def get_db():
    global _db
    if _db is None:
        raise RuntimeError(
            "Database is not initialized. Did you call init_db()?"
        )  # Changed to RuntimeError for clarity
    return _db


def get_users():
    global _users
    if _users is None:
        raise RuntimeError(
            "Users collection is not initialized. Did you call init_db()?"
        )  # Changed to RuntimeError for clarity
    return _users


def get_logs():
    global _logs
    if _logs is None:
        raise RuntimeError(
            "Logs collection is not initialized. Did you call init_db()?"
        )  # Changed to RuntimeError for clarity
    return _logs


async def close_db_connection():
    """
    Closes the MongoDB client connection if it exists.
    """
    global client
    if client:
        client.close()
        print("[MongoDB] Connection closed.")
        client = None
