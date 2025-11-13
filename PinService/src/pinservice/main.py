from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, File, Form, UploadFile

from .database import get_session
from .models import Pin
from .schemas import PinCreate


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def none():
    return {"message": "Hello World"}
