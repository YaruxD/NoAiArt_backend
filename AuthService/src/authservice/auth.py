from typing import Optional, Tuple
from fastapi import HTTPException, Depends, status
from jose import JWTError, jwt
from datetime import datetime, timedelta, timezone
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordBearer

from .database import get_session
from .settings import settings
from .models import User
from .security import verify_password


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")

JWT_PRIVATE_KEY = settings.JWT_PRIVATE_KEY
JWT_PUBLIC_KEY = settings.JWT_PUBLIC_KEY

ACCESS_TOKEN_EXPIRETIME = timedelta(minutes=15)
REFRESH_TOKEN_EXPIRETIME = timedelta(days=7)

async def create_access_token(data: dict) -> str:

    payload = {
        "username": data["username"],
        "user_id": data["user_id"],
        "exp": str(int((datetime.now(timezone.utc) + ACCESS_TOKEN_EXPIRETIME).timestamp())),
        "type": "access",
    }

    acces_token = jwt.encode(payload, key=JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)

    return acces_token

async def create_refresh_token(data: dict, db) -> str:

    expire_time = str(int((datetime.now(timezone.utc) + REFRESH_TOKEN_EXPIRETIME).timestamp()))

    payload = {
        "username": data["username"],
        "user_id": data["user_id"],
        "exp": expire_time,
        "type": "refresh",
        "refresh_token_version": data["refresh_token_version"]
    }

    refresh_token = jwt.encode(payload, key=JWT_PRIVATE_KEY, algorithm=settings.JWT_ALGORITHM)

    return refresh_token

async def validate_refresh_token(token: str, db):

    data = await decode_token(token)
    if data == None or data["type"] != "refresh":
        raise HTTPException(status_code=401, detail="Invalid token")
    
    user = await db.get(User, data["user_id"])

    if user.refresh_token_version != data["refresh_token_version"]:
        raise HTTPException(status_code=401, detail="Invalid token")

    return user



async def decode_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, JWT_PUBLIC_KEY, algorithms = [settings.JWT_ALGORITHM])
    except JWTError:
        return None



async def authuser(username, password, db):
    result = await db.execute(select(User).where(username == User.username))
    user = result.scalar()

    if not user or not await verify_password(password, user.hashed_password):
        raise HTTPException(status_code=400, detail="Invalid credentials")
    
    return user




async def get_current_user(
    token: str = Depends(oauth2_scheme),
):
    payload = await decode_token(token)

    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if payload.get("type") != "access":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token type",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_id = payload.get("user_id")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token payload",
            headers={"WWW-Authenticate": "Bearer"},
        )

    current_user = {"id": user_id, "username": payload.get("username")}

    if current_user is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    return current_user

