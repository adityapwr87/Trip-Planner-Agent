import requests
from langchain_core.tools import tool

from core.config import GEOAPIFY_API_KEY


@tool
def get_accommodation_options(
    destination: str,
    check_in_date: str,
    check_out_date: str,
    adults: int = 1,
) -> dict:
    """
    Fetch accommodation place options for a destination using Geoapify Places API.

    Geoapify returns hotel/stay places, not live room inventory or date-specific prices.
    The date range is preserved for itinerary context.
    """
    try:
        if not GEOAPIFY_API_KEY:
            return {
                "status": "error",
                "hotel_suggestions": [],
                "message": "GEOAPIFY_API_KEY is not configured",
            }

        lon, lat = _get_coordinates(destination)
        if lon is None or lat is None:
            return {
                "status": "error",
                "hotel_suggestions": [],
                "message": f"Could not find coordinates for {destination}",
            }

        places = _get_accommodation_places(lon=lon, lat=lat)
        hotel_suggestions = [
            _normalize_place(place, check_in_date, check_out_date)
            for place in places
        ]

        return {
            "status": "success",
            "destination": destination,
            "check_in_date": check_in_date,
            "check_out_date": check_out_date,
            "adults": adults,
            "hotel_suggestions": hotel_suggestions,
            "message": (
                "Accommodation place options fetched successfully. "
                "Live room availability and prices are not provided by Geoapify."
            ),
        }
    except Exception as exc:
        return {
            "status": "error",
            "hotel_suggestions": [],
            "message": f"Accommodation tool failure: {str(exc)}",
        }


def _get_coordinates(destination: str) -> tuple[float | None, float | None]:
    response = requests.get(
        "https://api.geoapify.com/v1/geocode/search",
        params={
            "text": destination,
            "limit": 1,
            "apiKey": GEOAPIFY_API_KEY,
        },
        timeout=15,
    )
    if response.status_code != 200:
        print(f"Geoapify geocode error {response.status_code}: {response.text}")
        return None, None

    features = response.json().get("features", [])
    if not features:
        return None, None

    lon, lat = features[0].get("geometry", {}).get("coordinates", [None, None])
    return lon, lat


def _get_accommodation_places(lon: float, lat: float) -> list[dict]:
    response = requests.get(
        "https://api.geoapify.com/v2/places",
        params={
            "categories": ",".join(
                [
                    "accommodation.hotel",
                    "accommodation.hostel",
                    "accommodation.guest_house",
                    "accommodation.apartment",
                    "accommodation.motel",
                ]
            ),
            "filter": f"circle:{lon},{lat},15000",
            "bias": f"proximity:{lon},{lat}",
            "limit": 20,
            "apiKey": GEOAPIFY_API_KEY,
        },
        timeout=20,
    )
    if response.status_code != 200:
        print(f"Geoapify places error {response.status_code}: {response.text}")
        return []

    return response.json().get("features", [])


def _normalize_place(place: dict, check_in_date: str, check_out_date: str) -> dict:
    properties = place.get("properties", {})
    lon, lat = place.get("geometry", {}).get("coordinates", [None, None])

    return {
        "name": properties.get("name") or "Accommodation option",
        "category": _get_primary_category(properties.get("categories", [])),
        "address": properties.get("formatted"),
        "city": properties.get("city"),
        "state": properties.get("state"),
        "country": properties.get("country"),
        "latitude": lat,
        "longitude": lon,
        "check_in_date": check_in_date,
        "check_out_date": check_out_date,
        "estimated_price": "Not available from Geoapify",
        "availability": "Not available from Geoapify",
        "contact": {
            "phone": properties.get("contact", {}).get("phone"),
            "website": properties.get("website"),
        },
        "source": "Geoapify Places API",
    }


def _get_primary_category(categories: list[str]) -> str:
    for category in categories:
        if category.startswith("accommodation."):
            return category

    return "accommodation"
