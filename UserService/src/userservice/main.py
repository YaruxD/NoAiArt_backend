from fastapi import FastAPI, HTTPException, status
from contextlib import asynccontextmanager
from .database import engine
from .rabbitmq.consumer_user_auth import RBCUserAuth
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    consume_task = asyncio.create_task(RBCUserAuth.start_consume())
    yield 
    consume_task.cancel()
    await RBCUserAuth.close()
    await engine.dispose()     



app = FastAPI(lifespan = lifespan)