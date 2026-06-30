from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from core.config import GROQ_MODEL
from langgraph_app.state import TripState
from langgraph_app.tools.maps_tool import get_transport_options


MAPS_AGENT_SYSTEM_PROMPT = """
You are the maps agent for an AI trip planner.
Your job is to call the get_transport_options tool with the trip origin and destination.
Do not answer from memory. Always use the tool.
"""


def maps_node(state: TripState) -> TripState:
    llm = ChatGroq(model=GROQ_MODEL, temperature=0).bind_tools([get_transport_options])

    user_prompt = (
        "Find transport options for this trip:\n"
        f"Origin: {state.get('source', 'Unknown')}\n"
        f"Destination: {state.get('destination', 'Unknown')}\n"
        f"Date: {state.get('start_date', 'Unknown')}"
    )

    response = llm.invoke(
        [
            SystemMessage(content=MAPS_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = get_transport_options.invoke(tool_call["args"])
        return {
            "route_options": tool_result.get("route_options", []),
            "transport_data": tool_result,
            "routes_message": _build_routes_message(tool_result),
        }

    return {
        "route_options": [],
        "transport_data": {
            "status": "error",
            "route_options": [],
            "message": "Maps agent failed to call tool.",
        },
        "routes_message": "I could not find route options right now.",
    }


def _build_routes_message(transport_data: dict) -> str:
    if transport_data.get("status") != "success":
        return transport_data.get("message", "I could not find route options right now.")

    route_count = len(transport_data.get("route_options", []))
    return f"I found {route_count} transport options for your trip."
