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
    """Initialize async MongoDB and Redis connections."""
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
    """Close async MongoDB and Redis connections."""
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
