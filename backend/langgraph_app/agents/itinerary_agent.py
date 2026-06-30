from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from core.config import GROQ_MODEL
from langgraph_app.state import TripState


class DaySchedule(BaseModel):
    day: int = Field(description="Day number of the trip.")
    date: str = Field(description="Date for this day in YYYY-MM-DD format.")
    title: str = Field(description="Short title for the day.")
    morning: str = Field(description="Morning plan with time, place, and reason.")
    noon: str = Field(description="Noon or afternoon plan with time, place, food/rest suggestions, and reason.")
    evening_or_night: str = Field(description="Evening or night plan with time, place, and reason.")
    estimated_day_cost: str = Field(description="Estimated cost for the day.")
    travel_notes: list[str] = Field(description="Important movement, route, or timing notes for the day.")
    backup_plan: str = Field(description="Backup plan for bad weather, delays, or closures.")


class ItineraryResponse(BaseModel):
    title: str = Field(description="Short trip title.")
    overview: str = Field(description="Brief overview of the itinerary strategy.")
    days: list[DaySchedule] = Field(description="Day-wise itinerary.")
    recommended_transport: str = Field(description="Best transport recommendation based on route data.")
    recommended_stay_area: str = Field(description="Best stay area or accommodation recommendation.")
    budget_notes: list[str] = Field(description="Budget guidance and cost notes.")
    weather_notes: list[str] = Field(description="Weather-aware planning notes.")
    final_tips: list[str] = Field(description="Useful final tips for the traveler.")


def itinerary_node(state: TripState) -> TripState:
    llm = ChatGroq(model=GROQ_MODEL, temperature=0.2)
    planner = llm.with_structured_output(ItineraryResponse)
    itinerary_data = planner.invoke(_build_itinerary_prompt(state))
    itinerary_text = _render_itinerary(itinerary_data)

    return {
        "itinerary_data": itinerary_data.model_dump(),
        "itinerary": itinerary_text,
        "itinerary_message": itinerary_text,
        "current_step": "itinerary_generated",
        "next_agent": "user_approval",
        "research_signature": _build_research_signature(state),
    }


def _build_itinerary_prompt(state: TripState) -> str:
    memory_str = f"- Long-term memory constraints: {state.get('long_term_memory', [])}\n" if state.get('long_term_memory') else ""
    return f"""
You are an expert travel itinerary planner.

Create the best possible day-wise itinerary using only the trip details and research data below.
The itinerary must be practical, accurate, weather-aware, route-aware, and budget-aware.

Trip details:
- Source: {state.get("source")}
- Destination: {state.get("destination")}
- Start date: {state.get("start_date")}
- End date: {state.get("end_date")}
- Travelers: {state.get("travelers")}
- Budget: {state.get("budget")}
- Pacing: {state.get("pacing")}
- Vibe: {state.get("vibe")}
- Diet: {state.get("diet")}
- Preferences: {state.get("preferences", [])}
{memory_str}- Stay preference: {state.get("stay_preference")}
- Transport preference: {state.get("transport_preference")}

User feedback or change request:
{state.get("user_feedback") or state.get("user_input")}

Research data:
- Weather data: {_compact_weather_data(state.get("weather_data", {}))}
- Route options: {_compact_route_options(state.get("route_options", []))}
- Activities: {_compact_activities(state.get("activities", []))}
- Accommodation options: {_compact_hotels(state.get("hotel_suggestions", []))}

Rules:
- Make the itinerary day-wise.
- Each day must be divided into morning, noon, and evening_or_night.
- Use realistic pacing based on the user's requested pacing preference. Do not overload a day if they want a relaxed trip.
- Strictly adhere to the user's travel vibe and dietary requirements when suggesting activities and food.
- Prefer outdoor activities when weather is good and indoor/low-risk activities when rain is likely.
- Use route data to recommend transport sensibly.
- Use accommodation data to suggest a stay area or option, but do not invent live prices if unavailable.
- If exact opening hours are uncertain, avoid claiming exact official timings.
- If the user asked for changes, regenerate the itinerary while reusing the same research data.
- Keep the plan polished and useful for a real traveler.
"""


def _render_itinerary(itinerary_data: ItineraryResponse) -> str:
    lines = [
        f"# {itinerary_data.title}",
        "",
        itinerary_data.overview,
        "",
        "## Day-wise itinerary",
    ]

    for day in itinerary_data.days:
        lines.extend(
            [
                "",
                f"### Day {day.day}: {day.date} - {day.title}",
                f"**Morning:** {day.morning}",
                "",
                f"**Noon:** {day.noon}",
                "",
                f"**Evening/Night:** {day.evening_or_night}",
                "",
                f"**Estimated day cost:** {day.estimated_day_cost}",
            ]
        )

        if day.travel_notes:
            lines.append("")
            lines.append("**Travel notes:**")
            for note in day.travel_notes:
                lines.append(f"- {note}")

        lines.extend(["", f"**Backup plan:** {day.backup_plan}"])

    lines.extend(
        [
            "",
            "## Recommendations",
            f"**Transport:** {itinerary_data.recommended_transport}",
            "",
            f"**Stay:** {itinerary_data.recommended_stay_area}",
        ]
    )

    if itinerary_data.weather_notes:
        lines.extend(["", "## Weather notes"])
        for note in itinerary_data.weather_notes:
            lines.append(f"- {note}")

    if itinerary_data.budget_notes:
        lines.extend(["", "## Budget notes"])
        for note in itinerary_data.budget_notes:
            lines.append(f"- {note}")

    if itinerary_data.final_tips:
        lines.extend(["", "## Final tips"])
        for tip in itinerary_data.final_tips:
            lines.append(f"- {tip}")

    lines.extend(
        [
            "",
            "Would you like to approve this itinerary, or should I change anything?",
        ]
    )

    return "\n".join(lines)


def _compact_weather_data(weather_data: dict) -> dict:
    weather_days = []
    for day in weather_data.get("data", [])[:5]:
        weather_days.append(
            {
                "date": day.get("date"),
                "climate": day.get("climate"),
                "rain_chance": day.get("rain_chance"),
                "max_temp": day.get("max_temp"),
                "min_temp": day.get("min_temp"),
            }
        )

    return {
        "status": weather_data.get("status"),
        "message": weather_data.get("message"),
        "days": weather_days,
    }


def _compact_route_options(route_options: list[dict]) -> list[dict]:
    selected_routes = _select_best_routes(route_options)
    compacted = []
    for route in selected_routes:
        compacted.append(
            {
                "mode": route.get("mode"),
                "route_name": route.get("route_name") or route.get("title"),
                "price": route.get("price") or route.get("estimated_cost"),
                "duration_hours": route.get("duration_hours"),
                "duration_text": route.get("duration_text"),
                "distance_km": route.get("distance_km"),
                "airline": route.get("airline"),
            }
        )
    return compacted


def _compact_activities(activities: list[dict]) -> list[dict]:
    selected_activities = sorted(
        activities,
        key=lambda activity: activity.get("priority", 0),
        reverse=True,
    )[:8]
    compacted = []
    for activity in selected_activities:
        compacted.append(
            {
                "name": activity.get("name"),
                "category": activity.get("category"),
                "best_time": activity.get("best_time"),
                "duration_hours": activity.get("duration_hours"),
                "estimated_cost": activity.get("estimated_cost"),
                "location_hint": activity.get("location_hint"),
                "weather_suitability": activity.get("weather_suitability"),
                "priority": activity.get("priority"),
            }
        )
    return compacted


def _compact_hotels(hotel_suggestions: list[dict]) -> list[dict]:
    compacted = []
    for hotel in hotel_suggestions[:5]:
        compacted.append(
            {
                "name": hotel.get("name"),
                "category": hotel.get("category"),
                "city": hotel.get("city"),
                "area_or_address": _shorten_address(hotel.get("address")),
                "estimated_price": hotel.get("estimated_price") or hotel.get("price_total"),
                "availability": hotel.get("availability"),
            }
        )
    return compacted


def _select_best_routes(route_options: list[dict]) -> list[dict]:
    selected = []
    seen_modes = set()

    sorted_routes = sorted(
        route_options,
        key=lambda route: route.get("score", float("inf")),
    )

    for route in sorted_routes:
        mode = route.get("mode")
        if mode in seen_modes:
            continue
        selected.append(route)
        seen_modes.add(mode)
        if len(selected) >= 4:
            break

    return selected


def _shorten_address(address: str | None) -> str | None:
    if not address:
        return None

    parts = [part.strip() for part in address.split(",") if part.strip()]
    return ", ".join(parts[:3])


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
