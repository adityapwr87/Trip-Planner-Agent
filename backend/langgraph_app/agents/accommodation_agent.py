from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from core.config import GROQ_MODEL
from langgraph_app.state import TripState
from langgraph_app.tools.accommodation_tool import get_accommodation_options


ACCOMMODATION_AGENT_SYSTEM_PROMPT = """
You are the accommodation agent for an AI trip planner.
Your job is to call the get_accommodation_options tool with destination, check-in date, check-out date, and number of adults.
Do not answer from memory. Always use the tool.
"""


def accommodation_node(state: TripState) -> TripState:
    llm = ChatGroq(model=GROQ_MODEL, temperature=0).bind_tools([get_accommodation_options])

    user_prompt = (
        "Find accommodation options for this trip:\n"
        f"Destination: {state.get('destination', 'Unknown')}\n"
        f"Check-in date: {state.get('start_date', 'Unknown')}\n"
        f"Check-out date: {state.get('end_date', 'Unknown')}\n"
        f"Adults: {state.get('travelers', 1)}"
    )

    response = llm.invoke(
        [
            SystemMessage(content=ACCOMMODATION_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = get_accommodation_options.invoke(tool_call["args"])
        return {
            "hotel_suggestions": tool_result.get("hotel_suggestions", []),
            "accommodation_data": tool_result,
            "accommodation_message": _build_accommodation_message(tool_result),
        }

    return {
        "hotel_suggestions": [],
        "accommodation_data": {
            "status": "error",
            "hotel_suggestions": [],
            "message": "Accommodation agent failed to call tool.",
        },
        "accommodation_message": "I could not fetch accommodation options right now.",
    }


def _build_accommodation_message(accommodation_data: dict) -> str:
    if accommodation_data.get("status") != "success":
        return accommodation_data.get("message", "I could not fetch accommodation options right now.")

    count = len(accommodation_data.get("hotel_suggestions", []))
    return f"I found {count} accommodation options for your stay."
