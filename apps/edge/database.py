from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI

# Global variables to store DB connections
client = None
db = None
edge_db = None
logs = None


async def init_db():
    """Asynchronously initialize MongoDB connection using Motor."""
    global client, db, edge_db, logs

    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=50,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            waitQueueTimeoutMS=5000,
        )
        # Check the connection by pinging the server
        await client.admin.command("ping")

        DB_NAME = "envybase"
        db = client[DB_NAME]
        edge_db = db["edge_functions"]
        logs = db["logs"]

        return True
    except ConnectionFailure as e:
        raise Exception(
            f"Failed to connect to MongoDB: {str(e)}. Please check your connection settings."
        ) from e


async def close_db_connection():
    """Close MongoDB connection (Motor cleans up automatically, but we can force close)."""
    global client
    if client:
        client.close()
        client = None
