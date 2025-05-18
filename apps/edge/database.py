from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI

# Global variables to store DB connections
client = None
db = None
edge_db = None
logs = None


async def init_db():
    """
    Asynchronously initializes the MongoDB connection and sets global database references.

    Establishes a connection to the MongoDB server using Motor, verifies connectivity, and assigns global variables for the database and key collections. Raises an exception if the connection fails.

    Returns:
        True if the connection is successfully established.

    Raises:
        Exception: If unable to connect to MongoDB.
    """
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
    """
    Closes the MongoDB client connection if it exists.

    Resets the global client reference to None after closing the connection.
    """
    global client
    if client:
        client.close()
        client = None
