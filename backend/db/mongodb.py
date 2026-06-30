import os
from motor.motor_asyncio import AsyncIOMotorClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = os.getenv("MONGO_DB_NAME", "trip_planner")

class MongoDB:
    client: AsyncIOMotorClient = None
    db = None

db = MongoDB()

def get_database():
    if db.client is None:
        db.client = AsyncIOMotorClient(MONGO_URI)
        db.db = db.client[DB_NAME]
    return db.db

def get_user_collection():
    return get_database()["users"]
