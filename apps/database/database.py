from motor.motor_asyncio import AsyncIOMotorClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI

# Async database references
client = None
db = None
users = None
database_db = None
logs = None
realtime = None


async def init_db():
    """
    Asynchronously initializes MongoDB and (optionally) Redis connections.

    Establishes a connection to the MongoDB server using the provided URI and sets up
    references to the main database and its collections. Verifies the MongoDB connection
    by issuing a ping command. Returns True if initialization succeeds. Raises an exception
    if the connection to MongoDB (or Redis, if enabled) fails.
    """
    global client, db, database_db, logs, realtime
    try:
        client = AsyncIOMotorClient(
            MONGO_URI,
            maxPoolSize=50,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            waitQueueTimeoutMS=5000,
        )

        # Verify MongoDB connection
        await client.admin.command("ping")

        # Setup Redis (optional: use sync redis if you prefer)
        # realtime = redis.Redis(host="localhost", port=6379, db=0)
        # if not await realtime.ping():
        #  raise ConnectionFailure("Redis connection failed")

        DB_NAME = "envybase"
        db = client[DB_NAME]
        database_db = db["database"]
        logs = db["logs"]

        return True
    except ConnectionFailure as e:
        raise Exception(f"Failed to connect to MongoDB or Redis: {str(e)}") from e


async def close_db_connection():
    """
    Closes the MongoDB and Redis connections if they are open.

    This function asynchronously closes the MongoDB client and Redis connection,
    resetting their global references to None.
    """
    global client, realtime
    if client:
        client.close()
        client = None
    if realtime:
        await realtime.close()
        realtime = None


# To run it on app startup:
# import this module in your FastAPI app
# and do: await init_db() inside FastAPI's startup event
