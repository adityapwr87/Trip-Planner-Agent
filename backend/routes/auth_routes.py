from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from typing import Any
from datetime import timedelta

from core.security import get_password_hash, verify_password, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from db.mongodb import get_user_collection
from models.user import UserCreate, UserResponse, Token, UserLogin
from bson import ObjectId

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=Token)
async def signup(user_in: UserCreate) -> Any:
    collection = get_user_collection()
    user = await collection.find_one({"email": user_in.email})
    if user:
        raise HTTPException(
            status_code=400,
            detail="The user with this email already exists in the system.",
        )
    
    hashed_password = get_password_hash(user_in.password)
    user_data = {
        "email": user_in.email,
        "full_name": user_in.full_name,
        "hashed_password": hashed_password
    }
    
    result = await collection.insert_one(user_data)
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(
            str(result.inserted_id), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }


@router.post("/login", response_model=Token)
async def login(form_data: UserLogin) -> Any:
    collection = get_user_collection()
    user = await collection.find_one({"email": form_data.email})
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect email or password")
    
    hashed_pwd = user.get("hashed_password")
    if not hashed_pwd or not verify_password(form_data.password, hashed_pwd):
        raise HTTPException(status_code=400, detail="Incorrect email or password")
        
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    
    return {
        "access_token": create_access_token(
            str(user["_id"]), expires_delta=access_token_expires
        ),
        "token_type": "bearer",
    }
