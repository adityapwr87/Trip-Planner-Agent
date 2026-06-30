import asyncio
from pydantic import BaseModel, Field
from langchain_groq import ChatGroq
from langchain_core.messages import HumanMessage, SystemMessage

from core.config import GROQ_MODEL
from langgraph_app.tools.weather_tool import get_weather
from langgraph_app.tools.maps_tool import get_transport_options
from langgraph_app.tools.activities_tool import get_activities
from langgraph_app.tools.accommodation_tool import get_accommodation_options

class CompareRequest(BaseModel):
    source: str | None = None
    destination_1: str
    destination_2: str
    start_date: str
    end_date: str
    travelers: int = 1
    budget: str | None = None
    preferences: str = ""

class ComparePoint(BaseModel):
    category: str = Field(description="Category of comparison, e.g., Weather, Cost, Activities, Accommodation")
    dest1_info: str = Field(description="Information for Destination 1")
    dest2_info: str = Field(description="Information for Destination 2")
    verdict: str = Field(description="Brief verdict on which destination wins this category and why")

class CompareResponse(BaseModel):
    winner: str = Field(description="The recommended destination based on the user's constraints")
    summary: str = Field(description="Overall summary of the comparison")
    comparison_points: list[ComparePoint] = Field(description="Detailed comparison points")

def _fetch_destination_data(dest: str, request: CompareRequest):
    weather = get_weather.invoke({
        "city": dest, 
        "start_date": request.start_date, 
        "end_date": request.end_date
    })
    
    routes = {}
    if request.source:
        routes = get_transport_options.invoke({
            "origin": request.source, 
            "destination": dest, 
            "date": request.start_date
        })

    activities = get_activities.invoke({
        "destination": dest, 
        "start_date": request.start_date, 
        "end_date": request.end_date,
        "preferences": [request.preferences] if request.preferences else [],
        "travelers": request.travelers,
        "budget": request.budget
    })

    accommodations = get_accommodation_options.invoke({
        "destination": dest, 
        "check_in_date": request.start_date, 
        "check_out_date": request.end_date, 
        "adults": request.travelers
    })

    return {
        "destination": dest,
        "weather": weather,
        "routes": routes,
        "activities": activities,
        "accommodations": accommodations
    }

def run_destination_comparison(request: CompareRequest) -> CompareResponse:
    # Since tools are synchronous, we'll just run them sequentially for now, 
    # or use a ThreadPoolExecutor. For simplicity and robustness, sequential is fine, 
    # but concurrent is better for performance.
    
    import concurrent.futures
    with concurrent.futures.ThreadPoolExecutor(max_workers=2) as executor:
        future_1 = executor.submit(_fetch_destination_data, request.destination_1, request)
        future_2 = executor.submit(_fetch_destination_data, request.destination_2, request)
        data_1 = future_1.result()
        data_2 = future_2.result()

    llm = ChatGroq(model=GROQ_MODEL, temperature=0.2)
    extractor = llm.with_structured_output(CompareResponse)
    
    prompt = f"""
You are an expert travel advisor. The user is deciding between {request.destination_1} and {request.destination_2}.
Trip Dates: {request.start_date} to {request.end_date}
Travelers: {request.travelers}
Budget: {request.budget}
Preferences: {request.preferences}

Here is the concrete data fetched for {request.destination_1}:
{data_1}

Here is the concrete data fetched for {request.destination_2}:
{data_2}

Compare the two destinations strictly based on the provided data and the user's preferences. Evaluate Cost (using routes and accommodations), Weather, Activities, and Accessibility.
Do not invent data that is not present in the fetched information.
Finally, declare a recommended "winner".
"""
    response = extractor.invoke([
        SystemMessage(content="You are a data-driven travel comparison agent."),
        HumanMessage(content=prompt)
    ])
    
    return response
