from fastapi import APIRouter, Query
from controllers.explore_controller import get_places
from controllers.compare_controller import CompareRequest, run_destination_comparison

router = APIRouter(prefix="/api/explore", tags=["Explore"])

@router.get("/places")
def places(
    location: str = Query(default="Delhi"),
    lat: float | None = Query(default=None),
    lon: float | None = Query(default=None),
):
    return get_places(location=location)

@router.post("/compare")
def compare_destinations(request: CompareRequest):
    return run_destination_comparison(request)
