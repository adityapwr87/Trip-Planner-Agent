from langgraph.checkpoint.mongodb import MongoDBSaver

from db.database import init_db, get_mongo_client
from langgraph_app.graph import build_trip_graph

# Initialize application DB (creates MongoDB indexes)
init_db()

# Initialize LangGraph checkpoint memory using MongoDB
client = get_mongo_client()
memory = MongoDBSaver(client)

trip_graph = build_trip_graph(memory)
