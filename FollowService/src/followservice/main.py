from contextlib import asynccontextmanager
from typing import List
from .rabbitmq.consumer_follow_auth import RBCFollowAuth
from fastapi import Depends, FastAPI, HTTPException, status
from pydantic import BaseModel
from neo4j import Session
from .database import get_session
from .service import SubscriptionService
import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    consume_task = asyncio.create_task(RBCFollowAuth.start_consume())
    yield 
    consume_task.cancel()
    await RBCFollowAuth.close()
    await engine.dispose()     

app = FastAPI(lifespan=lifespan)


class FollowRequest(BaseModel):
    follower_id: int
    following_id: int

class UserCreate(BaseModel):
    id: int
    username: str

@app.post("/create_user/")
async def create_user(user: UserCreate, session: Session = Depends(get_session)):
    service = SubscriptionService(session)
    try:
        service.create_user(user.id, user.username)
        return {"status": "user created"}
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e)
        )
    except Exception:
        raise HTTPException(
            status_code=500,
            detail="Internal server error"
        )

@app.post("/follow")
async def follow(data: FollowRequest, session: Session = Depends(get_session)):
    service = SubscriptionService(session)

    try:
        if data.follower_id == data.following_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="User cannot follow himself"
            )

        service.follow(data.follower_id, data.following_id)

        return {"status": "followed"}

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e)
        )

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.delete("/follow")
async def unfollow(data: FollowRequest, session: Session = Depends(get_session)):
    service = SubscriptionService(session)

    try:
        service.unfollow(data.follower_id, data.following_id)

        return {"status": "unfollowed"}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )


@app.get("/followers/{user_id}")
async def get_followers(user_id: int, session: Session = Depends(get_session)):
    service = SubscriptionService(session)

    try:
        followers = service.followers(user_id)
        return {"followers": followers}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get followers"
        )


@app.get("/following/{user_id}")
async def get_following(user_id: int, session: Session = Depends(get_session)):
    service = SubscriptionService(session)

    try:
        following = service.following(user_id)
        return {"following": following}

    except Exception:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to get following"
        )