from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from .auth import get_current_user
from .clients.auth_client import auth_client
from .clients.user_client import user_client
from .clients.comment_client import comment_client
from .schemas import RegistrationScheme, TokenScheme, UserRead, Profile, ProfileCard


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)

#AuthService

@app.post("/auth/register", response_model=UserRead, tags=["Auth"])
async def register_user(user_data: RegistrationScheme):
    try:
        return await auth_client.register(user_data=user_data)
    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(
            status_code=e.response.status_code, detail=error_json["detail"]
        )


@app.post("/auth/login",  tags=["Auth"], response_model=TokenScheme)
async def login(response: Response, user_data: OAuth2PasswordRequestForm = Depends()):
    try:
        data = await auth_client.login(user_data=user_data)
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        token_type = data.get("type", "bearer")

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=60 * 60 * 24 * 7,
        )

        return TokenScheme(access_token=access_token, token_type=token_type)
    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(
            status_code=e.response.status_code, detail=error_json["detail"]
        )


@app.post("/auth/refresh", tags=["Auth"], response_model=TokenScheme)
async def refresh_token(request: Request, response: Response):
    try:
        refresh_token = str(request.cookies.get("refresh_token"))
        data = await auth_client.refresh_token(refresh_token)
        access_token = data["access_token"]
        refresh_token = data["refresh_token"]
        token_type = data.get("type", "bearer")

        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,
            samesite="lax",
            secure=True,
            max_age=60 * 60 * 24 * 7,
        )

        return TokenScheme(access_token=access_token, token_type=token_type)

    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(
            status_code=e.response.status_code, detail=error_json["detail"]
        )


@app.get("/me")
async def read_me(current_user=Depends(get_current_user)):
    return current_user


#UserService
@app.get("/user/profile/{id}", tags=["Profile"], response_model=Profile, summary="Возвращает данные для основного профиля")
async def get_profile(id: int):
    try:
        return await user_client.get_profile(id)
    except httpx.HTTPStatusError as e:
        detail = {"detail": e.response.text or "Ошибка получения профиля"}
        raise HTTPException(status_code=e.response.status_code)

@app.get("/user/profile/card/{id}", tags=["Profile"], response_model=ProfileCard, summary="Возвращает данные карточки профиля")
async def get_profile_card(id: int):
    try:
        return await user_client.get_profile_card(id)
    except httpx.HTTPStatusError as e:
        detail = {"detail": e.response.text or "Ошибка получения профиля"}
        raise HTTPException(status_code=e.response.status_code)

@app.get("/get_comment/{pin_id}")
async def get_comments(
    pin_id: int, 
    limit: int = 3, 
    offset: int = 0,
    ):
    try:
        return await comment_client.get_comments(pin_id,limit,offset)
    except httpx.HTTPStatusError as e:
        detail = {"detail": e.response.text or "Ошибка получения коммента"}
        raise HTTPException(status_code=e.response.status_code)
