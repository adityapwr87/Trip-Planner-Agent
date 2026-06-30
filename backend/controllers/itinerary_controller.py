from uuid import uuid4

from langchain_core.messages import HumanMessage
from pydantic import BaseModel, Field

from db.database import save_session_metadata, get_user_email
from memory.graph_memory import trip_graph


class DirectItineraryRequest(BaseModel):
    source: str
    destination: str
    start_date: str
    end_date: str
    travelers: int = Field(gt=0)
    budget: str
    preference_prompt: str | None = None
    session_id: str | None = None
    user_id: str | None = "default_user"


def generate_direct_itinerary(request: DirectItineraryRequest, user_email: str = None):
    session_id = request.session_id or str(uuid4())
    config = {"configurable": {"thread_id": session_id}}
    preference_text = (request.preference_prompt or "").strip()

    user_input = (
        "Generate a complete itinerary from form input.\n"
        f"Source: {request.source}\n"
        f"Destination: {request.destination}\n"
        f"Start date: {request.start_date}\n"
        f"End date: {request.end_date}\n"
        f"Travellers: {request.travelers}\n"
        f"Budget: {request.budget}\n"
        f"User preferences: {preference_text or 'No extra preferences provided'}"
    )

    state = trip_graph.invoke(
        {
            "messages": [HumanMessage(content=user_input)],
            "user_input": user_input,
            "user_id": request.user_id,
            "email": user_email,
            "intent": "trip_planning",
            "current_step": "preferences_extracted",
            "next_agent": "supervisor_agent",
            "source": request.source,
            "destination": request.destination,
            "start_date": request.start_date,
            "end_date": request.end_date,
            "travelers": request.travelers,
            "budget": request.budget,
            "preferences": [preference_text] if preference_text else [],
            "missing_fields": [],
            "follow_up_question": None,
        },
        config=config,
    )

    title = f"{state.get('destination') or request.destination} Trip"
    save_session_metadata(session_id, title, request.user_id)

    return {
        "session_id": session_id,
        "response": state.get("assistant_response"),
        "state": _serialize_state(state),
    }


def _serialize_state(state: dict) -> dict:
    serialized = dict(state)
    serialized["messages"] = [
        {"role": message.type, "content": message.content}
        for message in state.get("messages", [])
    ]
    return serialized
