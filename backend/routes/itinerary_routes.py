from fastapi import APIRouter, Depends
from core.deps import get_current_user
from models.user import UserInDB

from controllers.itinerary_controller import (
    DirectItineraryRequest,
    generate_direct_itinerary,
)


router = APIRouter(prefix="/itinerary", tags=["itinerary"])


@router.post("/generate", response_model=None)
async def generate_itinerary_route(request: DirectItineraryRequest, user: UserInDB = Depends(get_current_user)):
    request.user_id = user.id
    return generate_direct_itinerary(request, user.email)
