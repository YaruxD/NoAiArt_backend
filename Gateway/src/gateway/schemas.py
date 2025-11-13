from pydantic import BaseModel, Field, EmailStr
from typing import Optional


#Схемы для AuthService
class RegistrationScheme(BaseModel):

    username: str = Field(max_length=40, min_length=4)
    name: str = Field(max_length=40, min_length=3)
    password: str = Field(min_length=8, max_length=40)
    email: EmailStr

class UserRead(BaseModel):
    id: int
    username: str
    email: EmailStr

    class Config:
        from_attributes = True

class TokenScheme(BaseModel):
    access_token: str
    token_type: str

class CurrentUser(BaseModel):
    id: int
    username: str

#Схемы для UserService
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
    
    class Config:
        from_attributes = True