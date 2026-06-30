from fastapi import HTTPException
from serpapi import GoogleSearch

from core.config import SERPAPI_KEY


PLACEHOLDER_IMAGE = "https://via.placeholder.com/300x400?text=No+Image"


def get_places(location: str):
    try:
        if not SERPAPI_KEY:
            return {
                "status": "error",
                "location": location,
                "places": [_fallback_place(location)],
                "message": "SERPAPI_KEY is not configured",
            }

        params = {
            "engine": "google",
            "q": f"top sights in {location}",
            "api_key": SERPAPI_KEY,
            "hl": "en",
            "gl": "in",
        }

        search = GoogleSearch(params)
        results = search.get_dict()
        places = []

        top_sights = results.get("top_sights", {}).get("sights", [])
        if top_sights:
            for index, sight in enumerate(top_sights):
                places.append(
                    {
                        "id": index,
                        "title": sight.get("title", ""),
                        "description": sight.get("description", ""),
                        "image": sight.get("thumbnail", PLACEHOLDER_IMAGE),
                        "rating": sight.get("rating", ""),
                        "distance": f"{round(1 + index * 0.5, 2)} km away",
                    }
                )
        elif "local_results" in results:
            for index, local in enumerate(results.get("local_results", [])):
                places.append(
                    {
                        "id": index,
                        "title": local.get("title", ""),
                        "description": local.get("type", ""),
                        "image": local.get("thumbnail", PLACEHOLDER_IMAGE),
                        "rating": local.get("rating", ""),
                        "distance": f"{round(1 + index * 0.5, 2)} km away",
                    }
                )

        if not places:
            places = [_fallback_place(location)]

        return {
            "status": "success",
            "location": location,
            "places": places,
        }
    except Exception as exc:
        print(f"Places Error: {exc}")
        raise HTTPException(status_code=500, detail=str(exc))


def _fallback_place(location: str) -> dict:
    return {
        "id": 1,
        "title": f"Explore {location}",
        "description": "Discover local attractions",
        "image": "https://via.placeholder.com/300x400?text=Explore+More",
        "distance": "Nearby",
    }
