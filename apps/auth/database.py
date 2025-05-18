from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI

# Globals to hold the database connection and collections
client = None
db = None
users = None
logs = None

async def init_db():
    """Asynchronously initialize database connection."""
    global client, db, users, logs

    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=50,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            waitQueueTimeoutMS=5000,
        )
        # Verify connection
        await client.admin.command("ping")

        DB_NAME = "envybase"
        db = client[DB_NAME]
        users = db["users"]
        logs = db["logs"]
        print("[MongoDB] Connection initialized successfully.")
    except ConnectionFailure as e:
        raise Exception(
            f"Failed to connect to MongoDB: {str(e)}. Please check your connection settings."
        ) from e

async def close_db_connection():
    """Asynchronously close the database connection."""
    global client
    if client:
        client.close()
        print("[MongoDB] Connection closed.")
        client = None
