from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from core.config import GROQ_MODEL
from langgraph_app.state import TripState
from langgraph_app.tools.activities_tool import get_activities


ACTIVITIES_AGENT_SYSTEM_PROMPT = """
You are the activities agent for an AI trip planner.
Your job is to call the get_activities tool with the destination, date range, preferences, travelers, and budget.
Do not answer from memory. Always use the tool.
"""


def activities_node(state: TripState) -> TripState:
    llm = ChatGroq(model=GROQ_MODEL, temperature=0).bind_tools([get_activities])

    memory_str = f"Long-term user constraints/memory: {state.get('long_term_memory', [])}\n" if state.get('long_term_memory') else ""

    user_prompt = (
        "Find activities for this trip:\n"
        f"Destination: {state.get('destination', 'Unknown')}\n"
        f"Start date: {state.get('start_date', 'Unknown')}\n"
        f"End date: {state.get('end_date', 'Unknown')}\n"
        f"Preferences: {state.get('preferences', [])}\n"
        f"{memory_str}"
        f"Travelers: {state.get('travelers')}\n"
        f"Budget: {state.get('budget')}"
    )

    response = llm.invoke(
        [
            SystemMessage(content=ACTIVITIES_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = get_activities.invoke(tool_call["args"])
        return {
            "activities": tool_result.get("activities", []),
            "activities_data": tool_result,
            "activities_message": _build_activities_message(tool_result),
        }

    return {
        "activities": [],
        "activities_data": {
            "status": "error",
            "activities": [],
            "message": "Activities agent failed to call tool.",
        },
        "activities_message": "I could not generate activity suggestions right now.",
    }


def _build_activities_message(activities_data: dict) -> str:
    if activities_data.get("status") != "success":
        return activities_data.get("message", "I could not generate activity suggestions right now.")

    count = len(activities_data.get("activities", []))
    return f"I found {count} activity ideas for your destination."
