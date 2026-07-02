from fastapi import APIRouter, Depends
from core.deps import get_current_user
from models.user import UserInDB

from controllers.chat_controller import (
    ChatRequest,
    ResumeRequest,
    chat,
    resume_chat,
    get_chat_history,
    health_check,
    list_sessions,
)


router = APIRouter()


router.add_api_route("/", health_check, methods=["GET"])

@router.get("/sessions")
async def get_sessions_route(user: UserInDB = Depends(get_current_user)):
    return list_sessions(user.id)

@router.get("/chat/{session_id}")
async def get_chat_history_route(session_id: str, user: UserInDB = Depends(get_current_user)):
    return get_chat_history(session_id, user.id)

@router.post("/chat", response_model=None)
async def chat_endpoint(request: ChatRequest, user: UserInDB = Depends(get_current_user)):
    request.user_id = user.id
    return chat(request, user.email)

@router.post("/chat/resume", response_model=None)
async def resume_chat_endpoint(request: ResumeRequest, user: UserInDB = Depends(get_current_user)):
    return resume_chat(request)
