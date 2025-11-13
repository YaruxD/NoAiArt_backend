from contextlib import asynccontextmanager

import httpx
from fastapi import Depends, FastAPI, HTTPException, Request, Response
from fastapi.security import OAuth2PasswordRequestForm

from .clients.auth_client import auth_client
from .schemas import RegistrationScheme, TokenScheme, UserRead


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/auth/register", response_model=UserRead)
async def register_user(user_data: RegistrationScheme):
    try:
        return await auth_client.register(user_data=user_data)
    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(
            status_code=e.response.status_code, detail=error_json["detail"]
        )


@app.post("/auth/login", response_model=TokenScheme)
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


@app.post("/auth/refresh", response_model=TokenScheme)
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
