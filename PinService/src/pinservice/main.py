from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, UploadFile

from .database import get_session
from .models import Pin
from .reopositories.s3storage import s3_client
from .schemas import PinCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def none(file: UploadFile, user_id=Form(), title=Form(), description=Form()):
    await s3_client.upload_pin_image(user_id=user_id, file=file)
    return {"message": "Hello World"}
