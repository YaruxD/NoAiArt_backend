from contextlib import asynccontextmanager
from typing import List
from fastapi import Depends, FastAPI, Form, HTTPException, status
from sqlalchemy import select
from .database import get_session
from .models import Comment
from ..commentservice import schemas
from sqlalchemy.ext.asyncio import AsyncSession


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/get_comments/{pin_id}", summary="получить все комменты к пину", response_model=List[schemas.CommentPin])
async def get_comments(
    pin_id: int, 
    limit: int, 
    offset: int, 
    db: AsyncSession = Depends(get_session)
    ):
    data = await db.execute(select(Comment).where(pin_id == Comment.pin_id).limit(limit).offset(offset))
    comments = data.scalars().all()
    if not comments:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return comments
