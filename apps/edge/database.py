from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI
import atexit

# Initialize with None so we can check if connection is established
client = None
db = None
users = None
edge_db = None
logs = None


def init_db():
    """Initialize database connection."""
    global client, db, edge_db, logs

    try:
        client = MongoClient(
            MONGO_URI,
            maxPoolSize=50,
            connectTimeoutMS=5000,
            serverSelectionTimeoutMS=5000,
            waitQueueTimeoutMS=5000,
        )
        # Verify connection
        client.admin.command("ping")

        # Database name defined as a constant until configuration is updated
        DB_NAME = "envybase"
        db = client[DB_NAME]
        edge_db = db["edge_functions"]
        logs = db["logs"]

        # Register cleanup function
        atexit.register(close_db_connection)

        return True
    except ConnectionFailure as e:
        raise Exception(
            f"Failed to connect to MongoDB: {str(e)}. Please check your connection settings."
        ) from e


def close_db_connection():
    """Close database connection."""
    global client
    if client:
        client.close()
        client = None


# Initialize connection on module import
init_db()
