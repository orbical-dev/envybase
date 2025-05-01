from pymongo import MongoClient
from pymongo.errors import ConnectionFailure
from config import MONGO_URI, REDIS_HOST, REDIS_PORT

try:
	client = MongoClient(MONGO_URI,
						maxPoolSize=50,
						connectTimeoutMS=5000,
						serverSelectionTimeoutMS=5000,
						waitQueueTimeoutMS=5000)
	# Verify connection
	client.admin.command('ping')
	db = client["wyra"] # This is the database name, you can't change it(for now, I need to talk to Zantex)
	users = db["users"]
except ConnectionFailure:
	raise Exception("Failed to connect to MongoDB. Please check your connection settings.")