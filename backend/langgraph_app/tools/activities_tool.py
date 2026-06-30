from langchain_core.tools import tool
from langchain_groq import ChatGroq
from pydantic import BaseModel, Field

from core.config import GROQ_MODEL


class Activity(BaseModel):
    name: str = Field(description="Name of the activity or attraction.")
    category: str = Field(description="Type of activity, such as adventure, food, nature, culture, shopping, nightlife, or relaxation.")
    description: str = Field(description="Short travel-friendly description.")
    best_time: str = Field(description="Best time of day to do this activity.")
    suggested_date: str | None = Field(default=None, description="Suggested date in YYYY-MM-DD format when useful.")
    duration_hours: float = Field(description="Approximate time needed in hours.")
    estimated_cost: str = Field(description="Approximate cost range in local currency.")
    location_hint: str = Field(description="Area, neighborhood, or nearby landmark.")
    weather_suitability: str = Field(description="Whether the activity is indoor, outdoor, or weather-flexible.")
    booking_required: bool = Field(description="Whether advance booking is usually recommended.")
    priority: int = Field(description="Priority from 1 to 5, where 5 is highly recommended.")


class ActivitiesResponse(BaseModel):
    activities: list[Activity] = Field(description="Recommended activities for the trip.")
    summary: str = Field(description="Short summary of the activity plan.")


@tool
def get_activities(
    destination: str,
    start_date: str,
    end_date: str,
    preferences: list[str] | None = None,
    travelers: int | None = None,
    budget: str | int | float | None = None,
) -> dict:
    """Generate structured activity recommendations for a destination and date range."""
    try:
        llm = ChatGroq(model=GROQ_MODEL, temperature=0.2)
        extractor = llm.with_structured_output(ActivitiesResponse)
        response = extractor.invoke(
            _build_activities_prompt(
                destination=destination,
                start_date=start_date,
                end_date=end_date,
                preferences=preferences or [],
                travelers=travelers,
                budget=str(budget) if budget is not None else None,
            )
        )

        activities = [activity.model_dump() for activity in response.activities]
        return {
            "status": "success",
            "destination": destination,
            "start_date": start_date,
            "end_date": end_date,
            "activities": activities,
            "summary": response.summary,
            "message": "Activities generated successfully.",
        }
    except Exception as exc:
        return {
            "status": "error",
            "activities": [],
            "message": f"Activities tool failure: {str(exc)}",
        }


def _build_activities_prompt(
    destination: str,
    start_date: str,
    end_date: str,
    preferences: list[str],
    travelers: int | None,
    budget: str | None,
) -> str:
    return f"""
You are an expert trip activity planner.

Recommend practical activities for this trip.

Trip details:
- Destination: {destination}
- Start date: {start_date}
- End date: {end_date}
- Travelers: {travelers}
- Budget: {budget}
- User preferences: {preferences}

Rules:
- Return 8 to 12 diverse activities.
- Prefer activities that realistically exist at the destination.
- Match the user's preferences when available.
- Include a mix of must-see attractions, food/local experiences, relaxed options, and backup indoor options.
- Keep estimated_cost as a readable string such as "Free", "INR 500-1000", or "INR 2000+ per person".
- If exact event schedules are uncertain, recommend general activities instead of inventing fake events.
- suggested_date may be null unless there is a strong reason to place it on a specific date.
"""
