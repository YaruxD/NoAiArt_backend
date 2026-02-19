from contextlib import asynccontextmanager
from typing import Optional
from fastapi import Depends, FastAPI, Form, HTTPException, UploadFile, Query, status
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List

from .database import get_session
from .models import Pin
from .reopositories.s3storage import s3_client
from .schemas import PinCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/", summary="создать пин")
async def create_pin(file: UploadFile,
    user_id: int = Form(...),
    title: str = Form(...),
    description: str = Form(...),
    cost: Optional[int] = Form(None),
    db: AsyncSession = Depends(get_session)
):
    url = await s3_client.upload_pin_image(user_id=str(user_id), file=file)
    
    new_pin = Pin(
        user_id=user_id,
        image_url=url,
        title=title,
        description=description,
        cost=cost if cost is not None else 0 
    )
    
    db.add(new_pin)
    await db.commit()
    await db.refresh(new_pin)
    
    return new_pin

class IdRequest(BaseModel):
    ids: List[int]



@app.post("/list_pins", summary="получить пины по списку id")
async def get_pins_batch(request: IdRequest, db: AsyncSession = Depends(get_session)):
    result = await db.execute(select(Pin).where(Pin.id.in_(request.ids)))
    return result.scalars().all()


