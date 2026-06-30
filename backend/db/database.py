import os
from datetime import datetime
from pymongo import MongoClient

MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")
DB_NAME = "trip_planner"

# Create a sync client for operations that need to be synchronous
# (like those called from synchronous routes and LangGraph)
client = MongoClient(MONGO_URI)
db = client[DB_NAME]

def init_db():
    # MongoDB creates collections lazily, but we can ensure indexes here
    db.sessions.create_index("session_id", unique=True)
    db.user_memory.create_index("user_id", unique=True)

def save_session_metadata(session_id: str, title: str, user_id: str):
    # Only update title if it's not empty
    update_data = {
        "updated_at": datetime.utcnow(),
        "user_id": user_id
    }
    if title:
        update_data["title"] = title
        
    db.sessions.update_one(
        {"session_id": session_id},
        {"$set": update_data},
        upsert=True
    )

def get_sessions(user_id: str):
    # Fetch sessions strictly for the logged-in user, sorted by updated_at descending
    cursor = db.sessions.find({"user_id": user_id}, {"_id": 0}).sort("updated_at", -1)
    sessions = []
    for doc in cursor:
        sessions.append({
            "session_id": doc.get("session_id"),
            "title": doc.get("title", "New Trip"),
            "updated_at": doc.get("updated_at", datetime.utcnow()).isoformat()
        })
    return sessions

def get_user_memory(user_id: str = "default_user") -> list[str]:
    doc = db.user_memory.find_one({"user_id": user_id})
    if doc and "preferences" in doc:
        return doc["preferences"]
    return []

def update_user_memory(new_prefs: list[str], user_id: str = "default_user"):
    current = get_user_memory(user_id)
    # Merge and keep unique
    merged = list(set(current + new_prefs))
    
    db.user_memory.update_one(
        {"user_id": user_id},
        {"$set": {"preferences": merged}},
        upsert=True
    )

def get_mongo_client():
    return client

from bson import ObjectId

def get_user_email(user_id: str) -> str | None:
    if not user_id or user_id == "default_user":
        return None
    try:
        user = db.users.find_one({"_id": ObjectId(user_id)})
        if user:
            return user.get("email")
    except:
        return None
    return None
