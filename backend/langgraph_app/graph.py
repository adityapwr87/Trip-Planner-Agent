from langgraph.graph import END, StateGraph

from langgraph_app.agents.accommodation_agent import accommodation_node
from langgraph_app.agents.activities_agent import activities_node
from langgraph_app.agents.itinerary_agent import itinerary_node
from langgraph_app.agents.maps_agent import maps_node
from langgraph_app.agents.preference_agent import extract_preferences
from langgraph_app.agents.response_agent import prepare_assistant_response
from langgraph_app.agents.supervisor_agent import supervise_trip_flow
from langgraph_app.agents.weather_agent import weather_node
from langgraph_app.agents.email_agent import email_node
from langgraph_app.state import TripState


def start_node(state: TripState) -> TripState:
    return {}


def build_trip_graph(memory_saver):

    graph = StateGraph(TripState)

    graph.add_node("start", start_node)

    graph.add_node(
        "supervisor_agent",
        supervise_trip_flow
    )

    graph.add_node(
        "preference_agent",
        extract_preferences
    )

    graph.add_node(
        "weather_agent",
        weather_node
    )

    graph.add_node(
        "maps_agent",
        maps_node
    )

    graph.add_node(
        "activities_agent",
        activities_node
    )

    graph.add_node(
        "accommodation_agent",
        accommodation_node
    )

    graph.add_node(
        "itinerary_agent",
        itinerary_node
    )

    graph.add_node(
        "email_agent",
        email_node
    )

    graph.add_node(
        "response_agent",
        prepare_assistant_response
    )

    # ==========================
    # ENTRY
    # ==========================

    graph.set_entry_point("start")

    graph.add_edge(
        "start",
        "supervisor_agent"
    )

    # ==========================
    # SUPERVISOR ROUTING
    # ==========================

    graph.add_conditional_edges(
        "supervisor_agent",
        _route_after_supervisor,
        {
            "preference_agent": "preference_agent",
            "weather_agent": "weather_agent",
            "maps_agent": "maps_agent",
            "activities_agent": "activities_agent",
            "accommodation_agent": "accommodation_agent",
            "itinerary_agent": "itinerary_agent",
            "email_agent": "email_agent",
            "response_agent": "response_agent",
        },
    )

    # ==========================
    # AFTER PREFERENCE EXTRACTION
    # ==========================

    graph.add_edge(
        "preference_agent",
        "supervisor_agent"
    )

    # ==========================
    # RESEARCH AGENTS
    # ==========================

    for agent in [
        "weather_agent",
        "maps_agent",
        "activities_agent",
        "accommodation_agent",
    ]:

        graph.add_conditional_edges(
            agent,
            _route_after_research,
            {
                "itinerary_agent": "itinerary_agent",
                "response_agent": "response_agent",
            },
        )

    # ==========================
    # FINAL STEPS
    # ==========================

    graph.add_edge(
        "itinerary_agent",
        "response_agent"
    )

    graph.add_edge(
        "email_agent",
        "response_agent"
    )

    graph.add_edge(
        "response_agent",
        END
    )

    return graph.compile(
        checkpointer=memory_saver
    )
def _route_after_supervisor(
    state: TripState,
) -> str | list[str]:

    next_agent = state.get(
        "next_agent"
    )

    if next_agent == "response_agent":
        return "response_agent"

    if next_agent == "preference_agent":
        return "preference_agent"

    if next_agent == "research_agents":

        return [
            "weather_agent",
            "maps_agent",
            "activities_agent",
            "accommodation_agent",
        ]

    if next_agent in [
        "weather_agent",
        "maps_agent",
        "activities_agent",
        "accommodation_agent",
    ]:
        return next_agent

    if next_agent == "itinerary_agent":
        return "itinerary_agent"

    if next_agent == "email_agent":
        return "email_agent"

    return "response_agent"


def _route_after_research(state: TripState) -> str:
    return "itinerary_agent"
