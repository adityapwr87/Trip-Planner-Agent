from pydantic import BaseModel, EmailStr, Field
from typing import Optional

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(..., min_length=6)

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class UserInDB(UserBase):
    id: str
    hashed_password: str

class UserResponse(UserBase):
    id: str

class Token(BaseModel):
    access_token: str
    token_type: str
