from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, Form

from .database import get_session
from .models import Comment


@asynccontextmanager
async def lifespan(app: FastAPI):
    yield


app = FastAPI(lifespan=lifespan)


@app.post("/")
async def none():
    return {"message": "Hello World"}
