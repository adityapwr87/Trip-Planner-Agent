from typing import Annotated, Any, TypedDict

from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages


class TripState(TypedDict, total=False):
    messages: Annotated[list[BaseMessage], add_messages]
    user_input: str
    intent: str
    long_term_memory: list[str]
    user_id: str
    source: str
    destination: str
    start_date: str
    end_date: str
    travelers: int
    budget: str
    pacing: str
    vibe: str
    diet: str
    preferences: list[str]
    missing_fields: list[str]
    follow_up_question: str
    current_step: str
    next_agent: str
    supervisor_message: str
    assistant_response: str
    weather_message: str
    routes_message: str
    activities_message: str
    accommodation_message: str
    itinerary_message: str
    weather_data: dict[str, Any]
    route_options: list[dict[str, Any]]
    activities_data: dict[str, Any]
    activities: list[dict[str, Any]]
    accommodation_data: dict[str, Any]
    hotel_suggestions: list[dict[str, Any]]
    itinerary_data: dict[str, Any]
    itinerary: str
    research_signature: str
    approved: bool
    email: str
    email_offered: bool
    email_sent: bool
    email_approved: bool
