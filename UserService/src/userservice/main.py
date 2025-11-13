from fastapi import FastAPI, HTTPException, status, Depends
from contextlib import asynccontextmanager
from .database import engine, get_session
from .rabbitmq.consumer_user_auth import RBCUserAuth
import asyncio
from sqlalchemy import select
from .models import User
from ..userservice import schemas
from sqlalchemy.ext.asyncio import AsyncSession

@asynccontextmanager
async def lifespan(app: FastAPI):
    consume_task = asyncio.create_task(RBCUserAuth.start_consume())
    yield 
    consume_task.cancel()
    await RBCUserAuth.close()
    await engine.dispose()     



app = FastAPI(lifespan = lifespan)


@app.get("/profile/{id}", summary="Возвращает все данные главной страницы профиля", response_model=schemas.Profile)
async def get_profile(id: int, db: AsyncSession = Depends(get_session)):
    profile = await db.get(User, id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return profile



@app.get("/profile/comment/{id}", summary="Возвращет данные профиля коммента", response_model=schemas.ProfileComment)
async def get_profile_comment(id: int, db: AsyncSession = Depends(get_session)):
    profile = await db.get(User, id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return profile

@app.get("/profile/card/{id}", summary="Возвращает данные карточки профиля", response_model=schemas.ProfileCard)
async def get_profile_card(id: int, db: AsyncSession = Depends(get_session)):
    profile = await db.get(User, id)
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"User {id} not found")
    return profile