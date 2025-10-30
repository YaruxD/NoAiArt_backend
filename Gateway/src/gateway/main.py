from fastapi import Depends, FastAPI, HTTPException
from contextlib import asynccontextmanager
from fastapi.security import OAuth2PasswordRequestForm
import httpx

from .schemas import TokenScheme, UserRead, RegistrationScheme
from .clients.auth_client import auth_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield

app = FastAPI(lifespan = lifespan)

@app.post("/auth/register", response_model=UserRead)
async def register_user(user_data: RegistrationScheme):
    try:
        return await auth_client.register(user_data=user_data)
    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(status_code=e.response.status_code, detail=error_json["detail"])

@app.post("/auth/login", response_model=TokenScheme)
async def login(user_data: OAuth2PasswordRequestForm = Depends()):
    try:
        return await auth_client.login(user_data=user_data)
    except httpx.HTTPStatusError as e:
        error_json = e.response.json()
        raise HTTPException(status_code=e.response.status_code, detail=error_json["detail"])