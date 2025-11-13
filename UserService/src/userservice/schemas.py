from pydantic import BaseModel
from typing import Optional

class Profile(BaseModel):
    username: str
    name: str
    posts: int
    followers: int 
    followed: int
    avatar_url: Optional[str] = None
    collections: int
    verificated: bool
    description: Optional[str] = None

    class Config:
        from_attributes = True


class ProfileComment(BaseModel):
    name: str
    avatar_url: str
    verificated: bool

class ProfileCard(BaseModel):
    name: str
    avatar_url: Optional[str] = None
    verificated: bool
    followers: int
    card_image1: Optional[str] = None
    card_image2: Optional[str] = None
    description: Optional[str] = None
