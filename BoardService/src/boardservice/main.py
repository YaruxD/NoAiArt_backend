from contextlib import asynccontextmanager
from typing import List
from fastapi import Depends, FastAPI, Form, HTTPException, status
from sqlalchemy import select
from .database import get_session
from .models import Board
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/get_boards")
async def get_boards(
    db: AsyncSession = Depends(get_session)
    ):
    data = await db.execute(select(Board))
    boards = data.scalars().all()
    if not boards:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return 
