import datetime
import os

import requests
from langchain_core.tools import tool
from serpapi import GoogleSearch

from core.config import SERPAPI_KEY


IATA_CODES = {
    "delhi": "DEL",
    "new delhi": "DEL",
    "mumbai": "BOM",
    "goa": "GOI",
    "bengaluru": "BLR",
    "bangalore": "BLR",
    "chennai": "MAA",
    "kolkata": "CCU",
    "hyderabad": "HYD",
    "pune": "PNQ",
    "jaipur": "JAI",
    "ahmedabad": "AMD",
    "kochi": "COK",
    "cochin": "COK",
    "lucknow": "LKO",
    "varanasi": "VNS",
    "manali": "KUU",
    "dehradun": "DED",
}


def compute_score(cost, duration):
    return round(cost * 0.6 + duration * 0.4, 2)


def get_iata_code(city_name: str) -> str:
    cleaned_city = city_name.strip().lower()
    return IATA_CODES.get(cleaned_city, city_name[:3].upper())


def get_coordinates(city_name):
    """Convert a city name to longitude and latitude using OpenStreetMap Nominatim."""
    try:
        url = "https://nominatim.openstreetmap.org/search"
        headers = {
            "User-Agent": os.getenv(
                "NOMINATIM_USER_AGENT",
                "TripPlannerChatbot/1.0",
            )
        }
        params = {
            "q": city_name,
            "format": "json",
            "limit": 1,
        }
        response = requests.get(url, headers=headers, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data:
            return float(data[0]["lon"]), float(data[0]["lat"])
    except Exception as exc:
        print(f"Geocoding Error for {city_name}: {exc}")

    return None, None


def get_flights(origin, destination, date):
    results = []

    rapidapi_key = os.getenv("RAPIDAPI_BOOKING_KEY")
    if not rapidapi_key:
        print("RAPIDAPI_BOOKING_KEY not configured, skipping flights.")
        return results

    date = _clean_date(date)
    from_id = f"{get_iata_code(origin)}.AIRPORT"
    to_id = f"{get_iata_code(destination)}.AIRPORT"

    try:
        import http.client
        import json
        
        conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")
        headers = {
            'x-rapidapi-key': rapidapi_key,
            'x-rapidapi-host': "booking-com15.p.rapidapi.com",
            'Content-Type': "application/json"
        }
        
        url = f"/api/v1/flights/searchFlights?fromId={from_id}&toId={to_id}&departDate={date}&pageNo=1&adults=1&sort=BEST&cabinClass=ECONOMY&currency_code=INR"
        conn.request("GET", url, headers=headers)
        res = conn.getresponse()
        data = res.read()
        json_data = json.loads(data.decode("utf-8"))
        
        if json_data.get("status") is False or "data" not in json_data:
            print(f"RapidAPI Flights Error: {json_data.get('message', 'Unknown error')}")
            return []
            
        flight_offers = json_data.get("data", {}).get("flightOffers", [])
        
        for flight in flight_offers[:6]:
            price_details = flight.get("priceBreakdown", {}).get("total", {})
            price = price_details.get("units", 0) + (price_details.get("nanos", 0) / 1e9)
            
            segments = flight.get("segments", [])
            if not segments:
                continue
                
            # totalTime is in seconds in the API response
            total_duration_minutes = sum(seg.get("totalTime", 0) for seg in segments) / 60.0
            duration_hours = total_duration_minutes / 60.0
            
            first_departure = segments[0].get("departureAirport", {}).get("code")
            final_arrival = segments[-1].get("arrivalAirport", {}).get("code")
            
            airline = "Unknown Airline"
            legs = segments[0].get("legs", [])
            if legs and legs[0].get("carriersData"):
                airline = legs[0]["carriersData"][0].get("name", "Unknown Airline")
            
            results.append(
                {
                    "mode": "flight",
                    "provider": "Booking.com (RapidAPI)",
                    "price": round(price, 2),
                    "duration_hours": round(duration_hours, 2),
                    "total_duration_minutes": round(total_duration_minutes),
                    "score": compute_score(price, duration_hours),
                    "flights": [],
                    "layovers": [],
                    "first_departure": first_departure,
                    "final_arrival": final_arrival,
                    "airline": airline,
                }
            )
            
    except Exception as exc:
        print("Flight Error:", exc)

    return results


    results = []

    if not SERPAPI_KEY:
        return results

    try:
        params = {
            "engine": "google",
            "q": f"trains from {origin} to {destination} on {date}",
            "api_key": SERPAPI_KEY,
        }

        search = GoogleSearch(params)
        data = search.get_dict()

        for idx, res in enumerate(data.get("organic_results", [])[:3]):
            snippet = res.get("snippet", "")
            title = res.get("title") or f"Train option {idx + 1}"

            results.append(
                {
                    "mode": "train",
                    "duration_hours": 10,
                    "duration_text": "~10 hrs",
                    "estimated_cost": 500,
                    "provider": "Google Search (SerpApi)",
                    "title": title,
                    "route_name": title,
                    "info": snippet,
                    "source_link": res.get("link"),
                    "is_primary": idx == 0,
                    "score": compute_score(500, 10),
                }
            )
    except Exception as exc:
        print("Train Error:", exc)

    return results


def get_road(origin, destination):
    results = []
    lon1, lat1 = get_coordinates(origin)
    lon2, lat2 = get_coordinates(destination)

    if not (lon1 and lat1 and lon2 and lat2):
        print("Could not resolve coordinates for routing.")
        return results

    try:
        url = (
            f"https://router.project-osrm.org/route/v1/driving/{lon1},{lat1};{lon2},{lat2}"
            "?overview=full&alternatives=true"
        )

        response = requests.get(url, timeout=12)
        if response.status_code != 200:
            return results

        data = response.json()

        if data.get("code") == "Ok":
            road_options = []
            for idx, route in enumerate(data.get("routes", [])[:4]):
                distance_km = route.get("distance", 0) / 1000.0
                duration_hours = route.get("duration", 0) / 3600.0
                estimated_cost = distance_km * 7.5

                road_options.append(
                    {
                        "mode": "road",
                        "provider": "OSRM (Free Open Source)",
                        "is_primary": False,
                        "estimated_cost": round(estimated_cost),
                        "duration_hours": round(duration_hours, 2),
                        "distance_km": round(distance_km, 2),
                        "score": compute_score(estimated_cost, duration_hours),
                        "route_name": f"Route {idx + 1}: {origin} to {destination}",
                        "encoded_polyline": route.get("geometry", ""),
                    }
                )

            if road_options:
                fastest_route = min(
                    road_options,
                    key=lambda option: option["duration_hours"],
                )
                fastest_route["is_primary"] = True
                results.extend(road_options)
    except Exception as exc:
        print(f"Road Search Warning (OSRM skipped): {exc}")

    return results


@tool
def get_transport_options(origin: str, destination: str, date: str) -> dict:
    """Fetch transport options including flight and road routes."""
    results = []

    results.extend(get_flights(origin, destination, date))
    results.extend(get_road(origin, destination))
    results.sort(key=lambda route: route["score"])

    return {
        "status": "success",
        "data": results,
        "route_options": results,
        "message": "Transport options fetched successfully",
    }


def _clean_date(date):
    if date and isinstance(date, str):
        if " " in date:
            date = date.split(" ")[0]
        if "T" in date:
            date = date.split("T")[0]

    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return date
    except (ValueError, TypeError):
        return (datetime.datetime.now() + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
