import os

from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from langgraph_app.state import TripState


class IntentSchema(BaseModel):
    intent: str = Field(description="Top-level intent. Must be one of: general, trip_planning, email.")
    reasoning: str = Field(description="Why this intent was chosen.")


def supervise_trip_flow(state: TripState) -> TripState:
    intent = _classify_intent(state)

    if intent == "email":
        return {
            "current_step": "sending_email",
            "next_agent": "email_agent",
            "intent": "email",
            "follow_up_question": None,
        }

    if intent == "trip_planning":
        if state.get("current_step") == "preferences_extracted":
            return _route_trip_planning_after_preferences(state)

        return {
            "current_step": "extracting_preferences",
            "next_agent": "preference_agent",
            "intent": "trip_planning",
            "follow_up_question": None,
        }


    return {
        "current_step": "general_response",
        "next_agent": "response_agent",
        "intent": "general",
        "follow_up_question": None,
    }


def _classify_intent(state: TripState) -> str:
    if _is_trip_planning_follow_up(state):
        return "trip_planning"

    user_input = state.get("user_input", "")
    llm = ChatGroq(model=os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile"), temperature=0)
    extractor = llm.with_structured_output(IntentSchema)

    prompt = f"""
Classify the latest user message into exactly one top-level intent.

Allowed intents:
- general: coding, DSA, education, current affairs, mathematics, science, casual chat, explanations, jokes, normal assistant questions, AND one-off travel utility requests such as weather, flights, or hotels without asking for a trip.
- trip_planning: creating an itinerary, modifying a trip plan, providing missing trip details, changing trip details, or asking for a complete travel plan.
- email: asking to send an email, confirming to send the itinerary to email, or providing an email address for the itinerary.

Rules:
- Return only the top-level intent. Do not return weather, flights, hotels, activities, or accommodation as intents.
- A complete topic change must override previous travel context.
- If the user is clearly answering a previous travel follow-up, keep the previous travel intent.

Current compact state:
{_compact_state_for_prompt(state)}

Latest user message:
{user_input}
"""
    try:
        result = extractor.invoke(prompt)
        intent = result.intent.strip().lower()
    except Exception:
        intent = "general"

    if intent not in {"general", "trip_planning", "email"}:
        return "general"

    return intent


def _route_trip_planning_after_preferences(state: TripState) -> TripState:
    missing_fields = state.get("missing_fields", [])
    if missing_fields:
        return {
            "current_step": "collecting_preferences",
            "next_agent": "user",
            "intent": "trip_planning",
        }

    current_signature = _build_research_signature(state)
    previous_signature = state.get("research_signature")

    if _has_research_data(state) and previous_signature == current_signature:
        return {
            "current_step": "regenerating_itinerary",
            "next_agent": "itinerary_agent",
            "user_feedback": state.get("user_input", ""),
            "supervisor_message": None,
            "intent": "trip_planning",
        }

    if _has_research_data(state) and not state.get("itinerary"):
        return {
            "current_step": "generating_itinerary",
            "next_agent": "itinerary_agent",
            "supervisor_message": None,
            "intent": "trip_planning",
        }

    return {
        "current_step": "researching_trip_data",
        "next_agent": "research_agents",
        "supervisor_message": None,
        "intent": "trip_planning",
    }



def _is_trip_planning_follow_up(state: TripState) -> bool:
    return bool(
        state.get("intent") == "trip_planning"
        and state.get("current_step") == "collecting_preferences"
        and state.get("missing_fields")
    )


def _compact_state_for_prompt(state: TripState) -> dict:
    return {
        "previous_intent": state.get("intent"),
        "current_step": state.get("current_step"),
        "next_agent": state.get("next_agent"),
        "missing_fields": state.get("missing_fields"),
        "follow_up_question": state.get("follow_up_question"),
        "source": state.get("source"),
        "destination": state.get("destination"),
        "start_date": state.get("start_date"),
        "end_date": state.get("end_date"),
        "travelers": state.get("travelers"),
        "budget": state.get("budget"),
        "recent_messages": [
            {"role": message.type, "content": message.content[:300]}
            for message in state.get("messages", [])[-4:]
        ],
    }


def _has_research_data(state: TripState) -> bool:
    return bool(
        state.get("weather_data")
        and state.get("route_options") is not None
        and state.get("activities") is not None
        and state.get("hotel_suggestions") is not None
    )


def _build_research_signature(state: TripState) -> str:
    parts = [
        state.get("source", ""),
        state.get("destination", ""),
        state.get("start_date", ""),
        state.get("end_date", ""),
        str(state.get("travelers", "")),
        state.get("budget", ""),
    ]
    return "|".join(parts)
