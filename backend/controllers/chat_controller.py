from uuid import uuid4

from langchain_core.messages import HumanMessage
from pydantic import BaseModel

from db.database import get_sessions, get_user_memory, save_session_metadata, get_user_email
from memory.graph_memory import trip_graph


class ChatRequest(BaseModel):
    message: str
    session_id: str | None = None
    user_id: str | None = "default_user"

class ResumeRequest(BaseModel):
    session_id: str
    approved: bool


def health_check():
    return {"status": "ok", "message": "Trip Planner backend is running"}


def list_sessions(user_id: str):
    return {"sessions": get_sessions(user_id)}


def get_chat_history(session_id: str, user_id: str):
    # Verify session belongs to user by checking metadata first
    from db.database import db
    session_meta = db.sessions.find_one({"session_id": session_id})
    if session_meta and session_meta.get("user_id") != user_id:
        # Prevent accessing someone else's trip
        return {"session_id": session_id, "messages": []}

    config = {"configurable": {"thread_id": session_id}}
    state = trip_graph.get_state(config)

    if not state or not state.values:
        return {"session_id": session_id, "messages": []}

    messages = state.values.get("messages", [])

    return {
        "session_id": session_id,
        "messages": [
            {"role": msg.type, "content": msg.content}
            for msg in messages
        ],
        "state": _serialize_state(state.values),
    }


def chat(request: ChatRequest, user_email: str = None):
    session_id = request.session_id or str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    user_id = request.user_id

    # Grab existing user memory and load it into the state automatically
    user_memory = get_user_memory(user_id)

    state = trip_graph.invoke(
        {
            "messages": [HumanMessage(content=request.message)],
            "user_input": request.message,
            "user_id": user_id,
            "long_term_memory": user_memory,
            "email": user_email,
        },
        config=config,
    )

    # Save session metadata for the sidebar
    destination = state.get("destination", "New Trip")
    title = f"{destination} Trip" if destination else "New Trip"
    save_session_metadata(session_id, title, user_id)

    # Check if interrupted
    current_graph_state = trip_graph.get_state(config)
    requires_approval = False
    if current_graph_state and current_graph_state.next and "email_agent" in current_graph_state.next:
        requires_approval = True

    return {
        "session_id": session_id,
        "response": state.get("assistant_response"),
        "state": _serialize_state(state),
        "requires_approval": requires_approval,
    }


def resume_chat(request: ResumeRequest):
    config = {"configurable": {"thread_id": request.session_id}}
    
    # Update the state with approval decision
    trip_graph.update_state(config, {"email_approved": request.approved})
    
    # Resume the graph
    state = trip_graph.invoke(None, config=config)
    
    return {
        "session_id": request.session_id,
        "response": state.get("assistant_response") if state else "Resumed successfully.",
        "state": _serialize_state(state) if state else {},
        "requires_approval": False,
    }


def _serialize_state(state: dict) -> dict:
    serialized = dict(state)
    serialized["messages"] = [
        {"role": message.type, "content": message.content}
        for message in state.get("messages", [])
    ]
    return serialized
