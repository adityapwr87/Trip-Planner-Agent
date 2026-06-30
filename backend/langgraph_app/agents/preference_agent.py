import os

from dotenv import load_dotenv
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from langgraph_app.state import TripState
from db.database import update_user_memory

load_dotenv(override=True)

REQUIRED_FIELDS = ["source", "destination", "start_date", "end_date", "travelers", "budget", "pacing", "vibe", "diet"]


class TripPreferenceExtraction(BaseModel):
    source: str | None = Field(default=None, description="Starting city or location.")
    destination: str | None = Field(default=None, description="Destination city or location.")
    start_date: str | None = Field(default=None, description="Trip start date in YYYY-MM-DD format.")
    end_date: str | None = Field(default=None, description="Trip end date in YYYY-MM-DD format.")
    travelers: int | str | None = Field(default=None, description="Number of people travelling.")
    budget: str | None = Field(default=None, description="Total trip budget with currency.")
    pacing: str | None = Field(default=None, description="Preferred travel pace (e.g., relaxed, packed).")
    vibe: str | None = Field(default=None, description="Travel interests/vibe (e.g., nature, history, nightlife).")
    diet: str | None = Field(default=None, description="Dietary restrictions (e.g., vegan, halal, none).")
    preferences: list[str] | None = Field(default=None, description="Any other specific trip preferences.")
    new_long_term_preferences: list[str] | None = Field(default=None, description="New permanent personal traits (e.g., 'I am vegetarian').")
    follow_up_question: str | None = Field(default=None, description="A single, polite, conversational question asking for any missing required details.")


def extract_preferences(state: TripState) -> TripState:
    if state.get("intent") != "trip_planning":
        return {}

    user_input = state.get("user_input", "")
    
    model = os.getenv("GROQ_MODEL", "llama-3.3-70b-versatile")
    llm = ChatGroq(model=model, temperature=0).with_structured_output(TripPreferenceExtraction)

    prompt = f"""
    Extract trip details from the latest user message. 
    If the message is not related to travel, leave all fields empty.
    Never invent values. Preserve existing values unless the user changes them.
    Convert dates to YYYY-MM-DD when possible.
    Ensure you capture the user's preferred pacing (relaxed/packed), vibe, and dietary restrictions.
    If any required fields are missing, craft a polite, conversational follow_up_question to gather them.

    Current State:
    {_format_state_for_prompt(state)}

    Latest User Message:
    {user_input}
    """

    extracted = llm.invoke(prompt)
    updates = {}

    # Save long-term memory
    if extracted.new_long_term_preferences:
        update_user_memory(extracted.new_long_term_preferences, user_id=state.get("user_id", "default_user"))
        current_memory = state.get("long_term_memory", [])
        updates["long_term_memory"] = list(set(current_memory + extracted.new_long_term_preferences))

    # Extract required fields
    fields = ["source", "destination", "start_date", "end_date", "travelers", "budget", "pacing", "vibe", "diet", "preferences"]
    for field in fields:
        value = getattr(extracted, field)
        if value is not None:
            if field == "travelers" and isinstance(value, str) and value.strip().isdigit():
                value = int(value.strip())
            updates[field] = value

    # Check for missing fields
    merged_state = {**state, **updates}
    missing_fields = [f for f in REQUIRED_FIELDS if not merged_state.get(f)]
    updates["missing_fields"] = missing_fields

    if missing_fields:
        fallback_q = f"Please share these missing trip details: {', '.join(missing_fields)}."
        updates["follow_up_question"] = extracted.follow_up_question or fallback_q
    else:
        updates["follow_up_question"] = None

    updates["current_step"] = "preferences_extracted"
    updates["next_agent"] = "supervisor_agent"

    return updates


def _format_state_for_prompt(state: TripState) -> dict:
    compact_fields = ["source", "destination", "start_date", "end_date", "travelers", "budget", "pacing", "vibe", "diet", "preferences"]
    return {field: state.get(field) for field in compact_fields if field in state}
