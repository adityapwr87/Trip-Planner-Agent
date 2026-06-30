from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from core.security import SECRET_KEY, ALGORITHM
from db.mongodb import get_user_collection
from models.user import UserInDB
from bson import ObjectId

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
        
    collection = get_user_collection()
    user = await collection.find_one({"_id": ObjectId(user_id)})
    if user is None:
        raise credentials_exception
    return UserInDB(
        id=str(user["_id"]),
        email=user["email"],
        full_name=user.get("full_name"),
        hashed_password=user["hashed_password"]
    )
