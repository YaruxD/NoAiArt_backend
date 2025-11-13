from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from .auth import (
    authuser,
    create_access_token,
    create_refresh_token,
    validate_refresh_token,
)
from .database import engine, get_session
from .models import User
from .rabbitmq.producer_user_auth import send_message_to_userservice
from .schemas import LogoutResponse, RegistrationScheme, TokenScheme, UserRead
from .security import hash_password


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield
    await engine.dispose()


app = FastAPI(lifespan=lifespan)


@app.post("/register/", summary="registration", response_model=UserRead)
async def create_user(
    user: RegistrationScheme, db: AsyncSession = Depends(get_session)
):
    result = await db.execute(
        select(User).where(
            (User.username == user.username) | (User.email == user.email)
        )
    )
    existing = result.scalar_one_or_none()

    if existing:
        if str(existing.username) == str(user.username):
            raise HTTPException(status_code=400, detail="Username already taken")
        else:
            raise HTTPException(status_code=400, detail="Email already taken")

    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=await hash_password(user.password),
    )

    db.add(new_user)

    await db.commit()
    await db.refresh(new_user)
    user_to_add = user.dict(exclude={"password", "email"})
    user_to_add["id"] = new_user.id
    await send_message_to_userservice(user_to_add)

    return new_user


@app.post("/login/", summary="login in", response_model=TokenScheme)
async def login(
    user_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_session),
):
    user = await authuser(user_data.username, user_data.password, db)

    access_token = await create_access_token(
        {"username": user.username, "user_id": user.id}
    )
    refresh_token = await create_refresh_token(
        {
            "username": user.username,
            "user_id": user.id,
            "refresh_token_version": user.refresh_token_version,
        },
        db,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post("/refresh/", summary="refresh pair of tokens", response_model=TokenScheme)
async def refresh_token(
    refresh_token: str = Form(...), db: AsyncSession = Depends(get_session)
):
    user = await validate_refresh_token(refresh_token, db)

    access_token = await create_access_token(
        {"username": user.username, "user_id": user.id}
    )
    refresh_token = await create_refresh_token(
        {
            "username": user.username,
            "user_id": user.id,
            "refresh_token_version": user.refresh_token_version,
        },
        db,
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@app.post(
    "/logout_from_all_devices/",
    summary="logout from all devices",
    response_model=LogoutResponse,
)
async def logout_from_all_devices(
    user_id: int, db: AsyncSession = Depends(get_session)
):
    user = await db.get(User, user_id)

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    user.refresh_token_version += 1

    await db.commit()
    await db.refresh(user)

    return LogoutResponse(
        message="Logged out from all devices",
        user_id=user.id,
        refresh_token_version=user.refresh_token_version,
    )
