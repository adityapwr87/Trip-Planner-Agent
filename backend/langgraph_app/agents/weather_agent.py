from langchain_core.messages import HumanMessage, SystemMessage
from langchain_groq import ChatGroq

from core.config import GROQ_MODEL
from langgraph_app.state import TripState
from langgraph_app.tools.weather_tool import get_weather


WEATHER_AGENT_SYSTEM_PROMPT = """
You are the weather agent for an AI trip planner.
Your job is to call the get_weather tool with the destination, start date, and end date.
Do not answer from memory. Always use the tool.
"""


def weather_node(state: TripState) -> TripState:
    llm = ChatGroq(model=GROQ_MODEL, temperature=0).bind_tools([get_weather])

    user_prompt = (
        "Fetch weather for this trip:\n"
        f"Destination: {state.get('destination', 'Unknown')}\n"
        f"Start date: {state.get('start_date', 'Unknown')}\n"
        f"End date: {state.get('end_date', 'Unknown')}"
    )

    response = llm.invoke(
        [
            SystemMessage(content=WEATHER_AGENT_SYSTEM_PROMPT),
            HumanMessage(content=user_prompt),
        ]
    )

    if response.tool_calls:
        tool_call = response.tool_calls[0]
        tool_result = get_weather.invoke(tool_call["args"])
        weather_succeeded = tool_result.get("status") in {"success", "partial"}

        return {
            "weather_data": tool_result,
            "weather_status": "weather_checked" if weather_succeeded else "weather_failed",
            "weather_message": _build_weather_message(tool_result),
        }

    return {
        "weather_data": {
            "status": "error",
            "data": [],
            "message": "Weather agent failed to call tool.",
        },
        "weather_status": "weather_failed",
        "weather_message": "I could not fetch weather data right now.",
    }


def _build_weather_message(weather_data: dict) -> str:
    if weather_data.get("status") == "partial":
        return (
            f"{weather_data.get('message')} "
            "I will continue with the available trip research."
        )

    if weather_data.get("status") != "success":
        return weather_data.get("message", "I could not fetch weather data right now.")

    return "I checked the weather for your trip."
